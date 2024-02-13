# pyright: reportMissingImports=false
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routes import chatroom_router, user_router, message_router, task_router

app = FastAPI()

# @app.get("/hello")
# def hello():
#     return {"message" : "안녕하세요!"}

origins = [
    'http://127.0.0.1:8000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 

app.include_router(user_router.router)
app.include_router(chatroom_router.router)
app.include_router(message_router.router)
app.include_router(task_router.router)