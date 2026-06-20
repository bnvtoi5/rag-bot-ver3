import os
import sys

# --- PHÒNG THỦ GIẢM TẢI RAM CHO MÁY 8GB (BẮT BUỘC ĐỂ TRÊN ĐẦU FILE) ---
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import operator
import re  # NÂNG CẤP: Thêm thư viện xử lý Regex để ép xuống dòng nguồn trích dẫn
import streamlit as st
from typing import Annotated, TypedDict, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Import cấu hình và mạng lưới Agent từ thư mục src/
from src.config import Config
from src.agents.graph import agent_app

# Import trực tiếp hàm xử lý từ file run_ingest.py
from run_ingest import main as run_ingestion_process

# Tải biến môi trường và kiểm tra API Key
load_dotenv()
if not os.getenv("GROQ_API_KEY"):
    st.error("LỖI: Chưa cấu hình GROQ_API_KEY trong file .env!")
    st.stop()

# Đảm bảo thư mục data đầu vào luôn tồn tại
if not os.path.exists(Config.RAW_DATA_DIR):
    os.makedirs(Config.RAW_DATA_DIR)

# --- CẤU HÌNH GIAO GIỆN STREAMLIT WEB UI ---
st.set_page_config(page_title="AI Multi-Agent RAG", page_icon="🤖", layout="wide")

# Khởi tạo trạng thái kiểm soát bộ nhớ trang (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False  # Trạng thái khóa ô chat khi AI đang chạy

# TÍCH HỢP MỚI: Khởi tạo trạng thái nút bấm dừng phản hồi
if "stop_clicked" not in st.session_state:
    st.session_state.stop_clicked = False

# NÂNG CẤP: Khởi tạo bộ đếm key để tự động xóa/reset khung file uploader
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Hàm Callback thay đổi trạng thái khi nhấn nút dừng
def click_stop_generation():
    st.session_state.stop_clicked = True

# --- THANH SIDEBAR: KÉO THẢ & CẤU HÌNH CHUNK SIZE ---
with st.sidebar:
    st.header("📂 Quản Lý Tài Liệu")
    
    # 1. Khung kéo thả file (Dùng thuộc tính key động để có thể tự động clear danh sách file)
    uploaded_files = st.file_uploader(
        "Kéo thả hoặc chọn file tài liệu của bạn:", 
        type=["txt", "pdf"], 
        accept_multiple_files=True,
        disabled=st.session_state.is_processing,
        key=f"file_uploader_{st.session_state.uploader_key}"
    )
    
    st.divider()
    
    # 2. Khu vực cấu hình thông số Băm nhỏ tài liệu (Chunking Configuration)
    st.subheader("⚙️ Cấu hình cấu trúc Vector")
    
    selected_chunk_size = st.slider(
        "Kích thước mảnh (Chunk Size):",
        min_value=200,
        max_value=2000,
        value=1200,
        step=100,
        help="Độ dài tối đa (số ký tự) của một mảnh văn bản khi băm nhỏ. Càng lớn ngữ cảnh càng sâu nhưng máy 8GB sẽ chạy nặng hơn."
    )
    
    selected_chunk_overlap = st.slider(
        "Độ trùng lặp (Chunk Overlap):",
        min_value=0,
        max_value=400,
        value=150,
        step=50,
        help="Số lượng ký tự được gối đầu trùng nhau giữa 2 mảnh liên tiếp để tránh mất ngữ cảnh ở ranh giới cắt."
    )
    
    if selected_chunk_overlap >= selected_chunk_size:
        st.warning("⚠️ Chú ý: Độ trùng lặp không nên lớn hơn hoặc bằng Kích thước mảnh!")
    
    st.divider()
    
    # 3. Nút bấm Xác nhận nạp dữ liệu
    if uploaded_files:
        st.info(f"Đang chờ xác nhận nạp {len(uploaded_files)} file...")
        
        if st.button("🚀 Xác Nhận Nạp Dữ Liệu", use_container_width=True, type="primary", disabled=selected_chunk_overlap >= selected_chunk_size):
            # THAY ĐỔI: Đổi chữ hiển thị thông báo nạp từ ChromaDB sang Qdrant
            with st.spinner("Đang tiến hành trích xuất và nhúng dữ liệu vào Qdrant DB..."):
                try:
                    # Ghi file tạm từ trình duyệt web vào thư mục data/ của dự án
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(Config.RAW_DATA_DIR, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # Gọi trực tiếp hàm xử lý và truyền tham số động từ UI xuống
                    is_success = run_ingestion_process(
                        chunk_size=selected_chunk_size, 
                        chunk_overlap=selected_chunk_overlap
                    )
                    
                    if is_success:
                        st.success(f"🎉 Thành công! Đã nạp dữ liệu với Chunk Size: {selected_chunk_size}, Overlap: {selected_chunk_overlap}")
                        
                        # NÂNG CẤP: Thay đổi uploader_key để ép Streamlit xóa sạch các file cũ khỏi khung chọn file!
                        st.session_state.uploader_key += 1
                        st.rerun() # Reload ngay lập tức để giao diện trống sạch sẽ
                    else:
                        st.error("❌ Không tìm thấy tài liệu hợp lệ hoặc có lỗi xảy ra trong quá trình đọc file.")
                        
                except Exception as e:
                    st.error(f"Lỗi hệ thống khi xử lý dữ liệu: {str(e)}")
    else:
        st.caption("Hãy tải file lên để kích hoạt nút xác nhận.")

    st.divider()
    # THAY ĐỔI: Đổi text thông tin chân trang (Storage: Qdrant Local)
    st.caption("UI: Streamlit | Orchestration: LangGraph | Storage: Qdrant Local | LLM: Llama 3.1")

# --- KHU VỰC HIỂN THỊ KHUNG CHAT CHÍNH ---
st.title("🤖 Trợ lý AI Doanh Nghiệp (Multi-Agent RAG)")
st.caption("Hệ thống phân tách tài nguyên và kiểm soát luồng xử lý thông minh")

# Hiển thị lịch sử các câu chat cũ ra màn hình (Đã tối ưu cấu trúc phân tách Expander và ép xuống dòng nguồn)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "---" in msg["content"]:
            # Tách chuỗi cũ để vẽ lại đúng cấu trúc giao diện sạch
            parts = msg["content"].split("---", 1)
            st.markdown(parts[0].strip())
            with st.expander("🔍 Xem chi tiết trích dẫn dòng gốc"):
                source_content = parts[1].strip()
                # NÂNG CẤP: Quét và ép bẻ dòng tại các vị trí, [1-3], [1, 2]... giúp giao diện lịch sử không bị dính liền
                formatted_source = re.sub(r'(\[\d+[\-,\d]*\])', r'\n\n\1', source_content)
                st.markdown(formatted_source.strip())
        else:
            st.markdown(msg["content"])

# Khung nhập câu hỏi (Tự động khóa hoàn toàn ô nhập khi AI đang bận xử lý)
user_query = st.chat_input(
    "Nhập câu hỏi tra cứu tài liệu nội bộ...", 
    disabled=st.session_state.is_processing
)

# Luồng xử lý khi người dùng nhấn gửi câu hỏi
if user_query:
    st.session_state.is_processing = True
    st.session_state.stop_clicked = False  # Reset trạng thái dừng phản hồi cho câu hỏi mới
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.rerun()

# Chạy luồng xử lý gọi mạng lưới Agent sau khi giao diện đã được khóa an toàn
if st.session_state.is_processing and len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user":
    current_query = st.session_state.messages[-1]["content"]

    with st.chat_message("assistant"):
        # TÍCH HỢP MỚI: Khối hiển thị nút Dừng phản hồi động nằm trên đầu khung trả lời của AI
        stop_button_placeholder = st.empty()
        with stop_button_placeholder:
            st.button("Dừng phản hồi", on_click=click_stop_generation, key="stop_gen_btn")
            
        # Khung trống hiển thị văn bản cập nhật liên tục (Streaming placeholder)
        response_placeholder = st.empty()
        full_answer = ""

        # CHUYỂN ĐỔI SANG STREAM: Đọc dữ liệu phân đoạn từ LangGraph thay vì invoke gọi cục bộ tốn thời gian
        try:
            for chunk in agent_app.stream({"messages": [{"role": "user", "content": current_query}]}):
                # BẮT ĐIỀU KIỆN NGẮT: Nếu phát hiện người dùng bấm nút Dừng phản hồi, bẻ gãy vòng lặp ngay lập tức
                if st.session_state.get("stop_clicked", False):
                    full_answer += "\n\n*Đã dừng phản hồi*"
                    break
                
                # Trích xuất dữ liệu từ các Node phát ra trong mạng lưới LangGraph
                if isinstance(chunk, dict):
                    # Lấy kết quả từ node cuối hoặc bất kỳ node nào ghi nhận thuộc tính final_answer
                    for node_value in chunk.values():
                        if isinstance(node_value, dict) and "final_answer" in node_value and node_value["final_answer"]:
                            full_answer = node_value["final_answer"]
                
                # Cập nhật hiển thị dòng chữ ra màn hình thời gian thực (Real-time feedback)
                if full_answer:
                    if "---" in full_answer:
                        parts = full_answer.split("---", 1)
                        response_placeholder.markdown(parts[0].strip())
                    else:
                        response_placeholder.markdown(full_answer)
        except Exception as stream_err:
            full_answer = f"❌ Đã xảy ra lỗi hệ thống trong quá trình xử lý luồng: {str(stream_err)}"
            response_placeholder.markdown(full_answer)

        # Xử lý dọn dẹp cấu hình sau khi hoàn thành luồng in chữ hoặc bấm Dừng
        stop_button_placeholder.empty()  # Xóa sạch nút Dừng phản hồi khỏi giao diện
        
        # Thiết lập cấu trúc vẽ khối Expander trích dẫn nếu có phần tách chuỗi '---'
        if "---" in full_answer:
            parts = full_answer.split("---", 1)
            main_answer = parts[0].strip()
            source_details = parts[1].strip()
            
            # Khóa hiển thị cố định ra màn hình sau khi luồng kết thúc
            response_placeholder.markdown(main_answer)
            with st.expander("🔍 Xem chi tiết trích dẫn dòng gốc"):
                # Thận trọng: Chỉ bẻ dòng nếu con số đó là định dạng số thứ tự trích dẫn (ví dụ: "1. ", "2. " hoặc nằm trong ngoặc)
                # Regex này bắt các số đứng đầu dòng hoặc sau dấu xuống dòng có dạng số thứ tự tài liệu
                formatted_source_details = re.sub(r'(\b\d+[\-,\d]*\.\s)', r'\n\n\1', source_details)
                st.markdown(formatted_source_details.strip())
        else:
            response_placeholder.markdown(full_answer)
        
        # Ghi nhận câu trả lời vào bộ nhớ lịch sử trang phục vụ vòng lặp render kế tiếp
        st.session_state.messages.append({"role": "assistant", "content": full_answer})
        
        # Mở khóa lại ô nhập chat input và ép đồng bộ làm mới trạng thái Streamlit
        st.session_state.is_processing = False
        st.rerun()
