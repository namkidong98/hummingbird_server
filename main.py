from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routes import user_router, chatroom_router, task_router, message_router
from database.database import db_connect, vector_connect

from chat_hummingbird.chatbot import Chatbot
from chat_hummingbird.generator.openai import OpenAIGenerator
from chat_hummingbird.summarizer.summarizer import Summarizer
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL")
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL") 


app = FastAPI()

origins = [
    'http://127.0.0.1:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

@app.on_event("startup")
def startup_db_client():
    app.client = db_connect()       # MongoDB 연결
    app.manager = vector_connect()   # ChromaDB 연결(vector search를 위해)

    app.generator = OpenAIGenerator(model_name=GENERATOR_MODEL, openai_api_key=OPENAI_API_KEY)
    app.summarizer = Summarizer(model_name=SUMMARIZER_MODEL)
    app.chatbot = chatbot = Chatbot(generator=app.generator, summarizor=app.summarizer, db_manager=app.manager)

@app.on_event("shutdown")
def shutdown_db_client():
    app.client.close()

app.include_router(user_router.router)
app.include_router(chatroom_router.router)
app.include_router(message_router.router)
app.include_router(task_router.router)