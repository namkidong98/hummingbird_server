from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routes import user_router, chatroom_router, task_router, message_router
from database.database import db_connect, vector_connect

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
    app.vector = vector_connect()   # ChromaDB 연결(vector search를 위해)

@app.on_event("shutdown")
def shutdown_db_client():
    app.client.close()

app.include_router(user_router.router)
app.include_router(chatroom_router.router)
app.include_router(message_router.router)
app.include_router(task_router.router)