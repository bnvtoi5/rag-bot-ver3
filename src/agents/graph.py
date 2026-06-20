import operator
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END

# Import thêm node chat thông thường mới tạo
from src.agents.supervisor import supervisor_node
from src.agents.rag_agent import rag_node
from src.agents.db_management import db_management_node
from src.agents.general_chat import general_chat_node  # <-- THÊM DÒNG NÀY

class AgentState(TypedDict):
    messages: Annotated[List[dict], operator.add]
    next_step: str
    context: str
    final_answer: str

def router(state: AgentState):
    return state["next_step"]

workflow = StateGraph(AgentState)

# Đăng ký thêm node general_chat
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("rag_agent", rag_node)
workflow.add_node("db_management", db_management_node)
workflow.add_node("general_chat", general_chat_node)  # <-- THÊM DÒNG NÀY

workflow.set_entry_point("supervisor")

# SỬA TẠI ĐÂY: Nếu supervisor trả về từ khóa "CHAT" thì đi sang node general_chat
workflow.add_conditional_edges(
    "supervisor", 
    router, 
    {
        "RAG": "rag_agent", 
        "DB_MANAGE": "db_management", 
        "CHAT": "general_chat"  # Đổi từ END thành general_chat
    }
)

# Sau khi các node xử lý xong xuôi thì mới kết thúc đồ thị (END)
workflow.add_edge("rag_agent", END)
workflow.add_edge("db_management", END)
workflow.add_edge("general_chat", END)  # <-- THÊM DÒNG NÀY

agent_app = workflow.compile()
