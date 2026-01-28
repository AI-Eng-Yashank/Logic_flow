import os
from dotenv import load_dotenv


load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

MODELS = {
    "router": "llama-3.1-8b-instant",
    "answer_generator": "llama-3.3-70b-versatile",
    "evaluator": "llama-3.1-8b-instant",
}
