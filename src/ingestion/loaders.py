import os
from langchain_core.documents import Document

def load_documents_from_folder(folder_path):
    documents = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return documents

    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        
        # 1. XỬ LÝ FILE TXT
        if file.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                full_text = f.read()  
            
            documents.append(Document(
                page_content=full_text,
                metadata={
                    "source": file,  # ĐỒNG BỘ: Chỉ lưu tên file thô, bỏ đường dẫn thư mục
                    "is_pdf": False,
                    "page": 1,
                    "location": "Trang 1" # Thêm trường vị trí phục vụ rag_agent.py hiển thị nguồn
                }
            ))
            
        # 2. XỬ LÝ FILE PDF (Sử dụng PyMuPDF để bóc tách trang chính xác tuyệt đối)
        elif file.endswith('.pdf'):
            import fitz  # Thư viện PyMuPDF
            
            try:
                doc_pdf = fitz.open(file_path)
                for page_num, page in enumerate(doc_pdf):
                    text = page.get_text()
                    page_actual = page_num + 1
                    
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "source": file,  # ĐỒNG BỘ: Chỉ lưu tên file thô, bỏ đường dẫn thư mục
                            "is_pdf": True,
                            "page": page_actual,
                            "location": f"Trang {page_actual}" # Định dạng vị trí rõ ràng cho LLM đọc
                        }
                    ))
                doc_pdf.close()
            except Exception as e:
                print(f"Lỗi khi đọc file PDF {file}: {e}")
                
        # 3. TÍCH HỢP THÊM: XỬ LÝ FILE WORD (.docx)
        elif file.endswith('.docx'):
            import docx2txt
            try:
                text = docx2txt.process(file_path)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "source": file,  # ĐỒNG BỘ: Chỉ lưu tên file thô
                        "is_pdf": False,
                        "page": 1,
                        "location": "Toàn bộ văn bản Word"
                    }
                ))
            except Exception as e:
                print(f"Lỗi khi đọc file Word {file}: {e}")
            
    return documents
