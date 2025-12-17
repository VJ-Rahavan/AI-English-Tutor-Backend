import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import uvicorn
from typing import Optional
from helper_functions import extract_json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LangChain Imports
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from prompts import EVALUATOR_PROMPT

# Configure API Key (Hardcoded for testing)
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
You are an English speaking tutor.

CRITICAL RULES:
- Respond ONLY with raw JSON
- DO NOT use markdown
- DO NOT use ```json
- DO NOT add explanations outside JSON
- The response must be valid JSON that can be parsed directly

Your tasks:
1. Respond naturally to what the user said (spoken English style).
2. If there is a grammar mistake, politely provide a correction.
3. Ask one short follow-up question.
4. Provide a polished, professional speaker version of the user's sentence.
5. Provide a slightly polished and simple version of the user's sentence.
6. Provide a casual, stylish, natural spoken-English version of the user's sentence.

VERY IMPORTANT CONSTRAINTS (for tasks 4, 5, and 6):
- Keep the SAME meaning as the user's sentence
- Do NOT summarize
- Do NOT generalize
- Do NOT explain the idea
- Do NOT turn it into an abstract statement
- Rewrite it as if the USER is speaking

Style guidance:
- Professional version: confident, professional, speaker-style sentence
- Simple polished version: minimal correction, everyday English
- Casual stylish version: relaxed, fluent, natural spoken English

JSON format:
{
  "reply": "string",
  "correction": {
    "hasMistake": true | false,
    "correctedSentence": "string",
    "explanation": "string"
  },
  "professionalVersion": "string",
  "simplePolishedVersion": "string",
  "casualStylishVersion": "string",
  "followUpQuestion": "string"
}

Rules:
- If there is no mistake, set hasMistake=false and keep correctedSentence and explanation empty.
- The advancedSentence must:
  - Be grammatically correct
  - Sound natural (not academic)
  - Be slightly more advanced than the user's sentence
- Keep all text concise and spoken-English friendly.
"""

session_score = 50
session_summary = "User is starting the conversation."

from pydantic import BaseModel

class ChatRequest(BaseModel):
    text: str

# Initialize LangChain Model
chat = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", convert_system_message_to_human=True)

@app.get("/")
def read_root():
    return {"message": "AI Tutor Backend is running (LangChain)"}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    global session_score
    global session_summary
    try:
        user_input = request.text
        
        if not user_input:
            raise HTTPException(status_code=400, detail="No input provided")

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_input)
        ]


        
        response = chat.invoke(messages)
        tutor_output = extract_json(response.content)

        # -------- STEP 2: Evaluator AI --------
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
        evaluation = extract_json(evaluation_response.content)
        

        # -------- STEP 3: Update score (deterministic logic) --------
        score_change = 0

        if evaluation["isGrammaticallyCorrect"]:
            score_change += 2
        else:
            score_change -= 1

        if evaluation["clarityScore"] >= 4:
            score_change += 1

        session_score = max(0, min(100, session_score + score_change))
        
        # -------- STEP 4: Merge response --------
        return {
            **tutor_output,
            "sessionFeedback": {
                "score": session_score,
                "change": score_change,
                "comment": evaluation["shortFeedback"]
            }
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
