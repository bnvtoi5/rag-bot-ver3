import json
import os
import time  # Giữ nguyên để cấu hình delay/retry API
from concurrent.futures import ThreadPoolExecutor 
from langchain_groq import ChatGroq
from src.config import Config

# THAY ĐỔI: Thay đổi import từ chroma_client sang qdrant_client
from src.database.qdrant_client import (
    get_all_uploaded_files as get_files_standalone, 
    delete_document_by_name,
    get_file_content_by_name
)

def invoke_chunk_summary(args):
    """Hàm gọi Groq có kiểm tra trạng thái dừng từ Streamlit để ngắt luồng ngầm"""
    llm, raw_summary_prompt, filename, chunk, idx = args
    
    # KIỂM TRA NGẮT: Nếu người dùng đã bấm dừng trên giao diện Streamlit, thoát luôn không gọi API nữa
    import streamlit as st
    if st.session_state.get("stop_clicked", False):
        print(f"-> Phân đoạn {idx+1} đã bị hủy bỏ do người dùng bấm Dừng.")
        return ""
        
    prompt = raw_summary_prompt.format(filename=f"{filename} (Phần {idx+1})", file_content=chunk)
    
    max_retries = 5  
    delay = 4        
    
    for attempt in range(max_retries):
        # Kiểm tra lại một lần nữa trước khi gửi
        if st.session_state.get("stop_clicked", False):
            return ""
            
        try:
            time.sleep(2) 
            return llm.invoke(prompt).content.strip()
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                time.sleep(5)
            else:
                break  
                
    return ""  

  
def split_text_into_chunks(text: str, max_chars: int = 8000) -> list[str]:
    """Chia nhỏ văn bản dài thành các đoạn nhỏ dựa trên số ký tự để tránh tràn giới hạn TPM của Groq"""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_length = 0
    
    for para in paragraphs:
        if current_length + len(para) > max_chars:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_length = len(para)
        else:
            current_chunk.append(para)
            current_length += len(para)
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
        
    return chunks


def db_management_node(state):
    messages = state["messages"]
    user_msg = messages[-1]["content"]
    
    # 1. Lấy danh sách file đang có trong database (Bây giờ lấy từ Qdrant payload)
    files = get_files_standalone()
    
    # Khởi tạo mô hình LLM
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=Config.GROQ_API_KEY, temperature=0)
    
    # 2. Đọc file prompt phân loại hành động
    manage_prompt_path = os.path.join("src", "prompts", "db_manage_prompt.txt")
    with open(manage_prompt_path, "r", encoding="utf-8") as f:
        raw_manage_prompt = f.read()
    
    prompt = raw_manage_prompt.format(files=files, user_msg=user_msg)
    
    try:
        ai_response = llm.invoke(prompt, response_format={"type": "json_object"}).content.strip()
        data = json.loads(ai_response)
        action = data.get("action")
    except Exception:
        action = "LIST" if "danh sách" in user_msg.lower() or "tài liệu" in user_msg.lower() else "NOT_FOUND"

    # 3. XỬ LÝ LOGIC NGHIỆP VỤ
    if action == "LIST":
        if not files:
            ai_msg = "Hiện tại hệ thống cơ sở dữ liệu đang trống, chưa có tài liệu nào."
        else:
            ai_msg = "Dưới đây là danh sách tài liệu đang có trong hệ thống:\n"
            for idx, f in enumerate(files, start=1):
                ai_msg += f"{idx}. {f}\n"
                
    elif action == "ANALYZE_FIELDS":
        if not files:
            ai_msg = "Cơ sở dữ liệu hiện đang trống nên tôi chưa thể xác định được các lĩnh vực kiến thức có thể hỗ trợ."
        else:
            analysis_prompt_path = os.path.join("src", "prompts", "db_analysis_prompt.txt")
            with open(analysis_prompt_path, "r", encoding="utf-8") as f:
                raw_analysis_prompt = f.read()
            analysis_prompt = raw_analysis_prompt.format(files=files, user_msg=user_msg)
            ai_msg = llm.invoke(analysis_prompt).content.strip()
                
    elif action == "SUMMARY":
        filename_to_summary = data.get("filename")
        if filename_to_summary in files:
            file_content = get_file_content_by_name(filename_to_summary)
            
            if not file_content.strip():
                ai_msg = f"Tài liệu '{filename_to_summary}' trống hoặc không chứa văn bản hợp lệ để tóm tắt."
            else:
                text_chunks = split_text_into_chunks(file_content, max_chars=8000)
                
                summary_prompt_path = os.path.join("src", "prompts", "db_summary_prompt.txt")
                with open(summary_prompt_path, "r", encoding="utf-8") as f:
                    raw_summary_prompt = f.read()
                
                print(f"-> Đang tóm tắt SONG SONG {len(text_chunks)} phân đoạn bằng đa luồng...")
                
                worker_args = [(llm, raw_summary_prompt, filename_to_summary, chunk, idx) for idx, chunk in enumerate(text_chunks)]
                
                with ThreadPoolExecutor(max_workers=1) as executor:
                    partial_summaries = list(executor.map(invoke_chunk_summary, worker_args))

                partial_summaries = [s for s in partial_summaries if s.strip()]
                
                if len(partial_summaries) > 1:
                    combined_text = "\n\n--- PHẦN TIẾP THEO ---\n\n".join(partial_summaries)
                    reduce_prompt = f"""
                    Bạn là một chuyên gia tổng hợp thông tin. Dưới đây là các bản tóm tắt thành phần của tài liệu '{filename_to_summary}'. 
                    Hãy kết hợp và biên soạn lại chúng thành một bản tóm tắt tổng thể duy nhất, mạch lạc, không trùng lặp ý.

                    Các bản tóm tắt thành phần:
                    {combined_text}

                    Yêu cầu kết quả:
                    - Trình bày rõ ràng bằng tiếng Việt theo cấu trúc: Tổng quan tài liệu -> Các nội dung cốt lõi chi tiết (gạch đầu dòng) -> Kết luận quan trọng.
                    - Giữ lại các số liệu quan trọng nếu có. Ngắn gọn, súc tích và chuyên nghiệp.
                    """
                    ai_msg = llm.invoke(reduce_prompt).content.strip()
                elif partial_summaries:
                    ai_msg = partial_summaries[0]
                else:
                    ai_msg = "Không thể tạo bản tóm tắt do lỗi xử lý mã token từ phía dịch vụ AI."
        else:
            ai_msg = "Không tìm thấy file bạn yêu cầu tóm tắt trong hệ thống. Vui lòng kiểm tra lại danh sách tài liệu."

    elif action == "DELETE":
        filename_to_delete = data.get("filename")
        if filename_to_delete in files:
            # THAY ĐỔI: Gọi hàm xóa tài liệu khỏi Qdrant (Hàm này sẽ định nghĩa trong qdrant_client.py)
            delete_document_by_name(filename_to_delete)
            
            # ĐÃ XÓA logic chromadb.PersistentClient() cũ không cần thiết
            ai_msg = f"Đã thực hiện xóa thành công toàn bộ dữ liệu của file '{filename_to_delete}' khỏi hệ thống Qdrant."
        else:
            ai_msg = f"Không tìm thấy tài liệu nào có tên khớp hoặc tương ứng với yêu cầu của bạn để xóa."
            
    else:
        ai_msg = "Yêu cầu quản lý dữ liệu không rõ ràng hoặc không tìm thấy file bạn chỉ định."

    new_message = {"role": "assistant", "content": ai_msg}
    return {
        "messages": [new_message],
        "final_answer": ai_msg
    }
