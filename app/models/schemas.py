from pydantic import BaseModel

class ChatRequest(BaseModel):
    text: str
    llm_provider: str = "gemini"
