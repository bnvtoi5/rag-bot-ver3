from langchain_groq import ChatGroq
from src.config import Config

def general_chat_node(state):
    """Xử lý các câu chào hỏi, tạm biệt hoặc nói chuyện phiếm thông thường"""
    messages = state["messages"]
    user_msg = messages[-1]["content"]
    
    llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=Config.GROQ_API_KEY, temperature=0.7)
    
    prompt = f"""
    Bạn là một trợ lý AI đĩnh đạc và thân thiện của doanh nghiệp. 
    Hãy phản hồi lại câu trò chuyện/chào hỏi dưới đây của người dùng một cách tự nhiên, lịch sự và ngắn gọn bằng tiếng Việt.
    Gợi ý thêm cho họ rằng họ có thể hỏi tra cứu tài liệu hoặc yêu cầu tóm tắt/xóa file nếu cần.

    Câu nói của người dùng: "{user_msg}"
    """
    
    ai_msg = llm.invoke(prompt).content.strip()
    
    new_message = {"role": "assistant", "content": ai_msg}
    return {
        "messages": [new_message],
        "final_answer": ai_msg
    }
