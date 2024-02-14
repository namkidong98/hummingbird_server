import os, sys
sys.path.append('../')
from dotenv import load_dotenv
import pymongo
from chat_hummingbird.vectordb.chroma_manager import ChromaManager

# .env 파일을 현재 작업 디렉토리에서 로드
load_dotenv() 

# 로드된 환경 변수 사용
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
HOST = os.getenv("VECTOR_HOST")
PORT = os.getenv("VECTOR_PORT")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# MongoDB 연결 시도
def db_connect():
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING) 
    except Exception:
        print("Error:", Exception)
    print("connect")
    return client

# ChromaDB 연결
def vector_connect():
    vector_client = ChromaManager(HOST, PORT, EMBEDDING_MODEL)
    return vector_client