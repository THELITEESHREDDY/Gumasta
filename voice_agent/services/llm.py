import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm_service = ChatGroq(
    model=os.environ["GROQ_MODEL"],
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0
)