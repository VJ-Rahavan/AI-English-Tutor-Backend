import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

# Configure API Key
if not os.getenv("GOOGLE_API_KEY") and os.getenv("GEMINI_API_KEY"):
     os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.3
)


# Initialize LangChain Model
chat = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", convert_system_message_to_human=True,temperature=0.3,
    top_p=0.9)
