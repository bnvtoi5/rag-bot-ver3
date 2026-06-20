import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, Filter, FieldCondition, MatchValue, MatchText, FilterSelector, TextIndexParams, TokenizerType
from langchain_qdrant import QdrantVectorStore
from src.config import Config
from src.database.embeddings import get_embedding_model

# ĐỒNG BỘ: Sử dụng tên bộ sưu tập cấu hình từ file config.py
COLLECTION_NAME = Config.COLLECTION_NAME

def get_raw_client() -> QdrantClient:
    """Khởi tạo kết nối trực tiếp lên cụm máy chủ Qdrant Cloud"""
    # SỬA LỖI TẠI ĐÂY: Loại bỏ hoàn toàn Config.CHROMA_DIR cũ, đọc trực tiếp cấu hình Cloud
    return QdrantClient(
        url=Config.QDRANT_URL,
        api_key=Config.QDRANT_API_KEY
    )


def get_vector_store() -> QdrantVectorStore:
    """Khởi tạo LangChain Qdrant VectorStore và tự động cấu hình bộ chỉ mục Index trên Cloud"""
    embeddings = get_embedding_model()
    client = get_raw_client()
    
    # 1. Tự động kiểm tra và khởi tạo collection nếu chưa tồn tại
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        sample_vector = embeddings.embed_query("init")
        vector_size = len(sample_vector)
        
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=vector_size, 
                distance=Distance.COSINE
            )
        )
        print(f"-> Đã khởi tạo thành công Collection '{COLLECTION_NAME}' trên Cloud.")
    
    # 2. SỬA LỖI CORE: Tự động cấu hình bộ chỉ mục Payload Index cho trường metadata.source
    # Để vượt qua chế độ Strict Mode của Qdrant Cloud khi gọi lệnh delete/filter
    try:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="metadata.source", # Đường dẫn trường cần lọc dữ liệu
            field_schema=TextIndexParams(
                type="text",
                tokenizer=TokenizerType.WHITESPACE, # Tách từ theo khoảng trắng để MatchText hoạt động tốt nhất
                lowercase=True
            )
        )
    except Exception as index_err:
        # Nếu index đã tồn tại sẵn, Qdrant sẽ báo lỗi nhẹ, chúng ta bypass qua an toàn
        pass

    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )




def get_all_uploaded_files() -> list[str]:
    """Tự động quét collection và lấy danh sách các tên file duy nhất từ payload trên Cloud"""
    try:
        client = get_raw_client()
        if not client.collection_exists(collection_name=COLLECTION_NAME):
            return []
            
        files = set()
        scroll_ids = None
        
        # Sử dụng cơ chế cuộn (scroll) dữ liệu của Qdrant để tối ưu bộ nhớ
        while True:
            records, scroll_ids = client.scroll(
                collection_name=COLLECTION_NAME,
                with_payload=True,
                with_vectors=False,
                limit=100,
                offset=scroll_ids
            )
            
            for point in records:
                # Mặc định LangChain lưu metadata trong dict `metadata` nằm bên trong payload
                meta = point.payload.get("metadata", {}) if point.payload else {}
                if meta and "source" in meta:
                    file_name = os.path.basename(meta["source"])
                    files.add(file_name)
                    
            if scroll_ids is None:
                break
                
        return list(files)
    except Exception as e:
        print(f"Lỗi khi lấy danh sách file từ Qdrant Cloud: {e}")
        return []



def delete_document_by_name(filename: str) -> bool:
    """Xóa sạch TOÀN BỘ dữ liệu thuộc về một file cụ thể ra khỏi Qdrant bằng bộ lọc chuẩn xác"""
    try:
        client = get_raw_client()
        if not client.collection_exists(collection_name=COLLECTION_NAME):
            return False
            
        # SỬA LỖI ĐÚNG GIAO DIỆN API: Sử dụng chính xác tham số 'points_selector'
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="metadata.source",
                            match=MatchText(text=filename) # Tìm kiếm chuỗi con chứa tên file
                        )
                    ]
                )
            ),
            wait=True # Ép hệ thống đồng bộ ngay lập tức qua internet quốc tế
        )
        print(f"✓ Đã thực hiện lệnh quét sạch toàn bộ dữ liệu của file {filename} khỏi Qdrant Cloud.")
        return True
    except Exception as e:
        print(f"Lỗi khi xóa file khỏi Qdrant Cloud: {e}")
        return False


    
def get_file_content_by_name(filename: str) -> str:
    """Lấy toàn bộ nội dung văn bản (page_content) hợp nhất của một file từ Qdrant"""
    try:
        client = get_raw_client()
        if not client.collection_exists(collection_name=COLLECTION_NAME):
            return ""
            
        full_text_list = []
        scroll_ids = None
        
        # Chỉ lấy các bản ghi có metadata.source khớp với tên file
        query_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.source",
                    match=MatchValue(value=filename)
                )
            ]
        )
        
        while True:
            records, scroll_ids = client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=query_filter,
                with_payload=True,
                with_vectors=False,
                limit=100,
                offset=scroll_ids
            )
            
            for point in records:
                if point.payload and "page_content" in point.payload:
                    full_text_list.append(point.payload["page_content"])
                    
            if scroll_ids is None:
                break
                
        # Nối tất cả các đoạn chunk lại thành một văn bản duy nhất
        return "\n\n".join(full_text_list)
    except Exception as e:
        print(f"Lỗi khi lấy nội dung file từ Qdrant Cloud: {e}")
        return ""
