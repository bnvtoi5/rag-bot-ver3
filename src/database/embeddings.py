from langchain_community.embeddings import HuggingFaceEmbeddings
from src.config import Config

def get_embedding_model():
    # Mô hình siêu nhẹ ~120MB, tối ưu hoàn hảo cho máy RAM 8GB
    return HuggingFaceEmbeddings(
        model_name=Config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'}
    )
