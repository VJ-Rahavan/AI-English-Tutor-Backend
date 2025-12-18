from langchain_core.messages import HumanMessage, SystemMessage
from app.prompts.tutor_prompt import SYSTEM_PROMPT
from app.utils.helper_functions import extract_json
from app.core.llm import llm as groq_model, chat as gemini_model

class TutorService:
    @staticmethod
    def get_tutor_response(user_input: str, llm_provider: str = "gemini"):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]
        
        selected_model = groq_model if llm_provider.lower() == "groq" else gemini_model
        response = selected_model.invoke(messages)
        return extract_json(response.content)
