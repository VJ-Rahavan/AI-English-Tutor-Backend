from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import chat
from app.prompts.evaluator_prompt import EVALUATOR_PROMPT
from app.utils.helper_functions import extract_json

class EvaluatorService:
    @staticmethod
    def evaluate_response(user_input: str, session_summary: str):
        evaluator_input = f"""
        Current sentence:
        {user_input}

        Session summary:
        {session_summary}
        """

        evaluator_messages = [
            SystemMessage(content=EVALUATOR_PROMPT),
            HumanMessage(content=evaluator_input)
        ]

        evaluation_response = chat.invoke(evaluator_messages)
        return extract_json(evaluation_response.content)
