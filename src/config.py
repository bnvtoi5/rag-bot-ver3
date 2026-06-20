import os
import streamlit as st
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

if os.getenv("HF_TOKEN"):
    os.environ["HF_TOKEN"] = os.getenv("HF_TOKEN")

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1" 

class Config:
    # Lấy Groq API Key
    try:
        GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    except Exception:
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        
    EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
        # Cấu hình Qdrant Cloud - Đọc trực tiếp từ file .env, không để lộ thông tin cứng trong code
    QDRANT_URL = os.getenv("QDRANT_URL")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    COLLECTION_NAME = "enterprise_rag"

    RAW_DATA_DIR = "./data/raw"
    
    @classmethod
    def validate(cls):
        if not cls.GROQ_API_KEY:
            raise ValueError("LỖI: Chưa cấu hình GROQ_API_KEY trong file .env!")
        if not cls.QDRANT_URL or not cls.QDRANT_API_KEY:
            raise ValueError("LỖI: Chưa cấu hình thông tin Qdrant Cloud!")
