from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

def split_docs(documents: List, chunk_size: int = 1200, chunk_overlap: int = 150) -> List:
    """
    Hàm băm nhỏ tài liệu nâng cấp:
    Sử dụng bản đồ hóa ký tự (Character Map) cho file TXT, phân tách trang độc lập cho PDF,
    và xử lý băm mảnh tự động cho văn bản DOCX, tối ưu hóa cho Qdrant Cloud.
    """
    # Cấu hình bộ băm mảnh văn bản của LangChain
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True 
    )
    
    final_chunks = []
    
    for doc in documents:
        # Trường hợp 1: Nếu là file PDF (Tính toán chính xác theo từng trang độc lập)
        if doc.metadata.get("is_pdf", False):
            chunks = text_splitter.split_documents([doc])
            for chunk in chunks:
                page_num = chunk.metadata.get("page", 1) 
                chunk.metadata["location"] = f"Vị trí: Trang {page_num}"
                final_chunks.append(chunk)
            continue
            
        # Trường hợp 2: Nếu là file WORD (.docx) - Băm mảnh tự động theo phân đoạn ngữ cảnh
        if doc.metadata.get("source", "").endswith('.docx'):
            chunks = text_splitter.split_documents([doc])
            for chunk in chunks:
                chunk.metadata["location"] = "Vị trí: Toàn bộ văn bản Word"
                if "start_index" in chunk.metadata:
                    del chunk.metadata["start_index"]
                final_chunks.append(chunk)
            continue
            
        # Trường hợp 3: Nếu là file TXT (Tính toán khoảng dòng chính xác tuyệt đối bằng line_map)
        orig_text = doc.page_content
        lines = orig_text.split('\n')
        
        # Tạo bản đồ dòng: ghi nhận vị trí ký tự đầu và kết thúc của từng dòng
        line_map = []
        current_idx = 0
        for i, line in enumerate(lines):
            start_idx = current_idx
            end_idx = current_idx + len(line)
            line_map.append((start_idx, end_idx, i + 1))  # Dòng hiển thị bắt đầu từ 1
            current_idx = end_idx + 1  # Cộng 1 để tính ký tự xuống dòng '\n'
            
        chunks = text_splitter.split_documents([doc])
        
        for chunk in chunks:
            chunk_start_char = chunk.metadata.get("start_index", 0)
            chunk_end_char = chunk_start_char + len(chunk.page_content)
            
            chunk_start_line = 1
            chunk_end_line = 1
            
            # Tra cứu vị trí ký tự đầu thuộc dòng nào trong bản đồ
            for start_idx, end_idx, line_num in line_map:
                if start_idx <= chunk_start_char <= end_idx:
                    chunk_start_line = line_num
                    break
                    
            # Tra cứu vị trí ký tự cuối thuộc dòng nào trong bản đồ
            for start_idx, end_idx, line_num in line_map:
                if start_idx <= max(start_idx, chunk_end_char - 1) <= end_idx:
                    chunk_end_line = line_num
                    break
            
            # ĐỒNG BỘ ĐỊNH DẠNG: Đồng bộ cấu trúc thông tin vị trí cho RAG Agent
            if chunk_start_line == chunk_end_line:
                chunk.metadata["location"] = f"Vị trí: Dòng {chunk_start_line}"
            else:
                chunk.metadata["location"] = f"Vị trí: Dòng {chunk_start_line}-{chunk_end_line}"
                
            # Dọn dẹp dữ liệu nháp để tránh thừa thãi khi lưu lên Qdrant Cloud
            if "start_index" in chunk.metadata:
                del chunk.metadata["start_index"]
                
            final_chunks.append(chunk)
            
    return final_chunks
