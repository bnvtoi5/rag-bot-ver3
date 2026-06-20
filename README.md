# Enterprise Multi-Agent RAG System 🤖📦

Hệ thống Chatbot tra cứu tài liệu nội bộ doanh nghiệp ứng dụng kiến trúc Đa tác nhân (Multi-Agent Workflow) qua **LangGraph**, lưu trữ vector cục bộ bằng **ChromaDB**, và vận hành tối ưu trên phần cứng văn phòng (**RAM 8GB**).
Link deploy streamlit: https://rag-chatbot-app-h3ewsswujfnxzfy46g5z8w.streamlit.app/

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Framework](https://img.shields.io/badge/LangGraph-Multi--Agent-orange)
![Database](https://img.shields.io/badge/ChromaDB-Local--Vector-green)
![OS](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS-lightgrey)

---

## 🛠️ Công Nghệ Sử Dụng

| Thành phần         | Công nghệ tích hợp | Chi tiết cấu hình                                            |
| :----------------- | :----------------- | :----------------------------------------------------------- |
| **Frontend UI**    | `Streamlit`        | Giao diện Web trực quan, thân thiện                          |
| **Orchestration**  | `LangGraph`        | Điều phối luồng tư duy Stateful Multi-Agent                  |
| **Storage**        | `ChromaDB`         | Cơ sở dữ liệu Vector lưu trữ vật lý cục bộ                   |
| **LLM Backbone**   | `Llama 3.1`        | Vận hành thông qua Groq API Cloud (Tốc độ cực cao)           |
| **Text Embedding** | `HuggingFace`      | Mô hình nhúng đa ngôn ngữ cục bộ (`paraphrase-multilingual`) |

---

## 📂 Cấu Trúc Thư Mục Dự Án (Project Structure)

```text
├── data/
│   ├── raw/            # Chứa file tài liệu mới tải lên (.txt, .pdf, .docx)
│   └── processed/      # Tự động lưu trữ file gốc sau khi nạp xong vào Qdrant
├── src/
│   ├── agents/          # Tầng logic tư duy và điều phối tác nhân AI (LangGraph)
│   │   ├── supervisor.py     # Agent trưởng phòng phân tích Intent điều phối luồng
│   │   ├── rag_agent.py      # Agent chuyên trách tra cứu tri thức tài liệu
│   │   ├── db_management.py  # Agent quản lý danh sách và xóa file tự động
│   │   └── graph.py          # Sơ đồ mạng lưới kết nối các Agent
│   ├── database/        # Tầng kết nối và cấu hình Vector DB
│   │   ├── qdrant_client.py  # Khởi tạo kết nối Qdrant Cloud (Tự động băm lô & lập chỉ mục)
│   │   └── embeddings.py     # Cấu hình mô hình nhúng văn bản (Chạy CPU tối ưu RAM 8GB)
│   ├── ingestion/       # Tầng tiền xử lý dữ liệu đầu vào
│   │   ├── loaders.py        # Quét và đọc cấu trúc file (.txt, .pdf, .docx)
│   │   └── splitter.py       # Băm nhỏ văn bản & Thuật toán ánh xạ dòng/trang chống ảo giác
│   ├── prompts/         # Quản lý tập trung hệ thống Prompt (Tách biệt khỏi Code)
│   │   ├── supervisor_prompt.txt
│   │   └── rag_prompt.txt
│   └── config.py        # Quản lý tập trung cấu hình hệ thống (Hỗ trợ Hybrid Local/.env/Secrets)
├── .env                 # Nơi cấu hình bảo mật API Key cá nhân (Đã chặn đẩy lên GitHub)
├── main.py              # Giao diện chính của ứng dụng (Streamlit Web UI + Real-time Streaming)
├── run_ingest.py        # Script xử lý nhúng và đẩy dữ liệu lên Qdrant Cloud theo lô (Batching)
├── setup.bat / setup_mac.sh # Script cài đặt môi trường tự động 1-click (Windows/Mac)
├── run.bat / run_mac.command # Script kích hoạt ứng dụng nhanh 1-click (Windows/Mac)
└── requirements.txt     # Danh sách các thư viện phần mềm bắt buộc cài đặt
```

---

## 📥 Tải Mã Nguồn (Chung cho cả hai hệ điều hành)
Tại trang GitHub này, bấm vào nút mã màu xanh Code (ở góc trên bên phải).

Chọn Download ZIP.

Sau khi tải xong, hãy giải nén file ZIP đó vào một thư mục trên máy tính của bạn.

---

## 🔑 Hướng dẫn tạo Groq API Key (Bắt buộc)

Để hệ thống có thể kết nối với mô hình Llama 3.1, bạn cần một API Key miễn phí từ Groq:

  ❇️ Truy cập vào trang: https://console.groq.com/
  
  ❇️ Đăng ký tài khoản (bằng Google hoặc Email).
  
  ❇️ Tại menu bên trái, chọn mục API Keys.
  
  ❇️ Bấm vào nút Create API Key.
  
  ❇️ Đặt tên cho Key (tên gì cũng được, ví dụ: MyRAGKey) và bấm Submit.
  
  ❇️ Copy đoạn mã đó lại ngay lập tức (vì nó chỉ hiển thị một lần duy nhất).

⚠️ LƯU Ý: Tuyệt đối không chia sẻ API Key này cho bất kỳ ai. Bạn dán nó vào Terminal lúc chạy file setup.bat hoặc setup_mac.command là được.

---

## 🔑 Hướng dẫn tạo Hugging Face Token (Bắt buộc)

Để hệ thống tự động tải mô hình nhúng văn bản (Embedding Model) về máy, bạn cần một mã Token miễn phí:

  ❇️ Truy cập vào trang: https://huggingface.co
  
  ❇️ Đăng ký hoặc đăng nhập vào tài khoản Hugging Face của bạn.
  
  ❇️ Nhấn vào nút **Create new token** (Tạo token mới).
  
  ❇️ Điền các thông tin cơ bản:
      - **Token name**: Đặt tên bất kỳ (Ví dụ: `rag-bot-token`).
      - **Token type**: Chọn quyền **Read** (Chỉ đọc) để bảo mật tốt nhất.
  
  ❇️ Kéo xuống cuối trang và nhấn nút **Generate token**.
  
  ❇️ Nhấn biểu tượng sao chép (Copy) đoạn mã token vừa sinh ra (Chuỗi có dạng bắt đầu bằng `hf_...`).

---

## 🔑 Hướng dẫn tạo tài khoản & Lấy cấu hình Qdrant Cloud (Bắt buộc)

Hệ thống RAG lưu trữ dữ liệu tập trung trên không gian đám mây quốc tế, bạn cần khởi tạo một phân vùng lưu trữ miễn phí:

  ❇️ Truy cập vào trang quản trị: https://qdrant.io
  
  ❇️ Đăng ký tài khoản mới (Khuyên dùng phương thức liên kết nhanh **Sign in with Google**).
  
  ❇️ Sau khi đăng nhập, tại mục **Clusters**, nhấn nút **Create Cluster** để tạo một cụm máy chủ miễn phí (Free Tier):
      - Giữ nguyên cấu hình mặc định (Môi trường Cloud miễn phí cung cấp sẵn 1GB RAM và 0.5 vCPU).
      - Nhấn **Create** và đợi khoảng 1-2 phút để hạ tầng đám mây tự động dựng cấu hình ngầm.
  
  ❇️ **Lấy thông tin đường dẫn kết nối (QDRANT_URL):**
      - Sau khi cụm máy chủ chuyển sang trạng thái hoạt động màu xanh lá cây, hãy tìm mục **Endpoint**.
      - Sao chép toàn bộ đường dẫn URL đó (Đường dẫn có dạng: `https://qdrant.io` hoặc không có cổng `:6333`).
  
  ❇️ **Tạo mã bảo mật truy cập dữ liệu (QDRANT_API_KEY):**
      - Tại thanh menu điều hướng bên trái giao diện web, nhấn vào mục **API Keys**.
      - Nhấn nút **Create API Key**.
      - Chọn đúng tên Cluster bạn vừa khởi tạo ở bước trên và bấm **Create**.
      - Sao chép (Copy) chuỗi API Key dài xuất hiện trên màn hình ngay lập tức (Vì hệ thống chỉ hiển thị nó một lần duy nhất).
      
---

## 🪟 Hướng Dẫn Cài Đặt & Khởi Chạy Trên Windows
⚠️ Yêu cầu hệ thống: Máy tính cần cài đặt sẵn Python 3.10+ và bắt buộc phải tích chọn mục "Add Python to PATH" trong quá trình cài đặt.

🔹 1. Quy trình cài đặt lần đầu

Bước 1.1: Truy cập vào thư mục dự án đã giải nén, tìm và nhấp đúp chuột vào file setup.bat.

Bước 1.2: Màn hình console màu đen sẽ hiện ra -> Bạn hãy dán mã GROQ_API_KEY của mình vào -> Nhấn Enter.

Bước 1.3: Chờ hệ thống tự động thiết lập môi trường ảo (.venv) và tải thư viện. Khi màn hình hiện thông báo [THANH CONG], bạn có thể tắt cửa sổ đó đi.

🔹 2. Quy trình chạy ứng dụng hàng ngày

Bước 2.1: Nhấp đúp chuột vào file run.bat.

Bước 2.2: Hệ thống sẽ khởi động nền tảng Web và tự động mở trình duyệt tại địa chỉ: http://localhost:8501.

---

## 🍏 Hướng Dẫn Cài Đặt & Khởi Chạy Trên MacOS
⚠️ Yêu cầu hệ thống: Máy tính cần cài đặt sẵn Python 3.10+.

🔸 1. Cấp quyền thực thi file (Bắt buộc làm lần đầu)
Do cơ chế bảo mật của macOS bảo vệ nghiêm ngặt các file tải từ Internet, bạn cần mở khóa hai file chạy theo các bước sau:

Bước 1.1: Mở ứng dụng Terminal trên máy Mac.

Bước 1.2: Gõ lệnh cd <dấu cách> Kéo và thả thư mục dự án của bạn vào cửa sổ Terminal -> Nhấn Enter.

Bước 1.3: Nhập lệnh trong terminal: 
```bash
chmod +x setup_mac.command run_mac.command
```
🔸 2. Quy trình cài đặt lần đầu

Bước 2.1: Nhấp đúp chuột vào file setup_mac.command.

Bước 2.2: Khi màn hình Terminal hiện yêu cầu nhập Key -> Dán mã GROQ_API_KEY của bạn vào -> Nhấn Enter.

Bước 2.3: Chờ hệ thống cài đặt tự động. Sau khi hoàn tất thành công, bạn có thể đóng tab Terminal này lại.

🔸 3. Quy trình chạy ứng dụng hàng ngày

Bước 3.1: Nhấp đúp chuột vào file run_mac.command.

Bước 3.2: Giao diện ứng dụng Streamlit sẽ tự động được mở trên trình duyệt Safari hoặc Chrome của bạn.

---

## 🚀 Hướng Dẫn Sử Dụng App
Sau khi hệ thống đã khởi chạy thành công tại địa chỉ http://localhost:8501, bạn hãy thực hiện theo các bước sau để bắt đầu tra cứu:

❇️ Bước 1: Import tài liệu vào app

Tại thanh menu bên trái, nhấn vào nút "Upload Documents".

Chọn các file tài liệu của bạn (PDF, Docx, hoặc Txt). Hệ thống sẽ tự động quét và phân tích nội dung.

❇️ Bước 2: Thiết lập câu hỏi

Tại khung chat chính, nhập câu hỏi hoặc yêu cầu cần tra cứu liên quan đến tài liệu đã nạp.

Hệ thống với kiến trúc Multi-Agent sẽ tự động phân tích và tìm kiếm câu trả lời chính xác nhất.

❇️ Bước 3: Nhận phản hồi

Kết quả sẽ hiển thị ngay lập tức kèm theo nguồn trích dẫn từ tài liệu của bạn (đảm bảo tính minh bạch và độ tin cậy).

💡 Mẹo: Bạn có thể hỏi theo ngôn ngữ tự nhiên (Tiếng Việt hoặc Tiếng Anh). Hệ thống sẽ tự động điều chỉnh ngữ cảnh phù hợp với nội dung doanh nghiệp của bạn.

---

## ⚙️ TỐI ƯU HÓA TÀI LIỆU (CHUNK SETTINGS)
Để hệ thống đạt độ chính xác cao nhất, bạn có thể điều chỉnh các thông số kỹ thuật trong file cấu hình (hoặc tại thanh sidebar):

❇️ Chunk Size (Kích thước đoạn cắt):

Khuyên dùng: 500 - 1000 ký tự.

Tại sao: Nếu quá lớn, mô hình dễ bỏ lỡ chi tiết; nếu quá nhỏ, ngữ cảnh có thể bị rời rạc. Hãy bắt đầu với 800 để có sự cân bằng tốt nhất.

❇️ Chunk Overlap (Đoạn chồng lấp):

Khuyên dùng: 10% - 20% của Chunk Size (khoảng 50 - 150).

Tại sao: Việc giữ lại một phần nội dung ở cuối đoạn trước cho đoạn sau giúp mô hình duy trì ngữ cảnh xuyên suốt, tránh tình trạng thông tin bị cắt đứt giữa chừng.

💡 Mẹo: Nếu tài liệu của bạn là văn bản pháp luật hoặc kỹ thuật nhiều thuật ngữ chuyên môn, hãy chọn Chunk Size nhỏ (khoảng 500) và Overlap lớn (khoảng 150) để đảm bảo tính liên kết tối đa.
