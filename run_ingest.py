import os
import shutil

# Ép cấu hình chạy 1 luồng duy nhất để bảo vệ máy RAM 8GB tuyệt đối không bị đơ/treo
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from src.config import Config
from src.ingestion.loaders import load_documents_from_folder
from src.ingestion.splitter import split_docs 
from src.database.qdrant_client import get_vector_store

def move_files_to_processed():
    """Hàm tự động di chuyển toàn bộ file từ thư mục raw sang processed"""
    raw_dir = Config.RAW_DATA_DIR
    processed_dir = "./data/processed"
    
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        
    files = os.listdir(raw_dir)
    moved_count = 0
    
    for file_name in files:
        if file_name.endswith('.txt') or file_name.endswith('.pdf') or file_name.endswith('.docx'):
            source_path = os.path.join(raw_dir, file_name)
            destination_path = os.path.join(processed_dir, file_name)
            
            if os.path.exists(destination_path):
                base, extension = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(destination_path):
                    file_name = f"{base}_backup_{counter}{extension}"
                    destination_path = os.path.join(processed_dir, file_name)
                    counter += 1
            
            shutil.move(source_path, destination_path)
            moved_count += 1
            print(f"-> Đã di chuyển: {file_name} sang thư mục /data/processed/")
            
    return moved_count

def main(chunk_size=1200, chunk_overlap=150):
    """
    Hàm xử lý nạp dữ liệu chính.
    Nhận tham số động chunk_size và chunk_overlap từ giao diện Streamlit.
    """
    print("=== BẮT ĐẦU TIẾN TRÌNH NẠP DỮ LIỆU TỰ ĐỘNG ===")
    print(f"-> Cấu hình băm: Chunk Size = {chunk_size} | Chunk Overlap = {chunk_overlap}")
    
    # 1. Đọc tài liệu từ thư mục dữ liệu thô
    print(f"Đang quét file trong thư mục {Config.RAW_DATA_DIR}...")
    docs = load_documents_from_folder(Config.RAW_DATA_DIR)
    if not docs:
        print("❌ Không tìm thấy tài liệu mới nào để nạp thêm!")
        return False
        
    # 2. Băm nhỏ tài liệu mới thông qua hàm đã sửa lỗi
    print(f"Đang tiến hành băm nhỏ {len(docs)} tài liệu mới...")
    chunks = split_docs(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"-> Đã băm xong thành {len(chunks)} đoạn nhỏ.")
    
    # THÀNH PHẦN THÊM MỚI: Chuẩn hóa metadata.source thành tên file thuần túy
    # Giúp hàm delete_document_by_name và get_all_uploaded_files của Qdrant hoạt động chính xác
    for chunk in chunks:
        if "source" in chunk.metadata:
            chunk.metadata["source"] = os.path.basename(chunk.metadata["source"])
    
    # 3. Nạp thêm dữ liệu vào Qdrant cục bộ (Đổi text log từ ChromaDB sang Qdrant)
    print(f"Đang tiến hành nhúng và nạp thêm vào Qdrant Vector DB...")
    vector_store = get_vector_store()
    vector_store.add_documents(chunks)
    print("✓ Đã lưu thành công dữ liệu mới vào Qdrant.")
    
    # 4. Kích hoạt tính năng tự động dọn dẹp file đầu vào
    print("Đang tiến hành dọn dẹp thư mục đầu vào...")
    total_moved = move_files_to_processed()
    
    print(f"🎉 HOÀN THÀNH MỸ MÃN! Đã nạp thêm thành công và lưu kho {total_moved} file gốc.")
    return True

if __name__ == "__main__":
    # Chạy mặc định nếu kích hoạt file độc lập bằng lệnh terminal
    main()
