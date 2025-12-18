from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest
from app.services.tutor_service import TutorService
from app.services.evaluator_service import EvaluatorService
from app.services.session_service import session_service

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_input = request.text
        if not user_input:
            raise HTTPException(status_code=400, detail="No input provided")

        print(user_input)
        # Tutor
        tutor_output = TutorService.get_tutor_response(user_input, request.llm_provider)

        # Evaluator
        # summary = session_service.get_summary()
        # evaluation = EvaluatorService.evaluate_response(user_input, summary)

        # Session Update
        # feedback = session_service.update_score(evaluation)

        return {
            **tutor_output,
            # "sessionFeedback": feedback
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
