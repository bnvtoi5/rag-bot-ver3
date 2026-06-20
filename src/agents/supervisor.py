import os
from langchain_groq import ChatGroq
from src.config import Config

def supervisor_node(state):
    # Khởi tạo LLM với temperature=0 để phân loại phân nhánh một cách chính xác nhất
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=Config.GROQ_API_KEY, temperature=0)
    user_msg = state["messages"][-1]["content"]
    
    # Đọc prompt từ thư mục prompts/
    prompt_path = os.path.join("src", "prompts", "supervisor_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        raw_prompt = f.read()
    
    # Truyền câu hỏi của người dùng vào prompt
    prompt = raw_prompt.format(user_msg=user_msg)
    response = llm.invoke(prompt).content.strip().upper()
    
    # Phân luồng thông minh dựa trên kết quả trả về của LLM
    if "DB_MANAGE" in response or "DELETE" in response or "LIST" in response or "SUMMARY" in response:
        chosen_step = "DB_MANAGE"
    elif "RAG" in response:
        chosen_step = "RAG"
    else:
        chosen_step = "CHAT"
        
    # Trả về kết quả bước đi kế tiếp để hàm điều hướng có điều kiện (Conditional Edge) trong Graph kích hoạt
    return {"next_step": chosen_step}
