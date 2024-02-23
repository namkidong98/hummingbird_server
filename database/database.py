import os, sys
sys.path.append('../')
from dotenv import load_dotenv
from pymongo import MongoClient
from chat_hummingbird.vectordb.chroma_manager import ChromaManager

# .env 파일을 현재 작업 디렉토리에서 로드
load_dotenv() 

# Mongo DB
CONNECTION_STRING = os.getenv("CONNECTION_STRING")  

# Chroma DB
HOST = os.getenv("VECTOR_HOST")
PORT = os.getenv("VECTOR_PORT")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# MongoDB 연결
def db_connect():
    client = None
    try:
        client = MongoClient(CONNECTION_STRING) 
    except Exception:
        print("Error:", Exception)
    print("connect")
    return client

# ChromaDB 연결
def vector_connect():
    manager = ChromaManager(HOST, PORT, EMBEDDING_MODEL)
    return manager