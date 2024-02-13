import os, sys
sys.path.append('../')
from dotenv import load_dotenv
import pymongo

# .env 파일을 현재 작업 디렉토리에서 로드
load_dotenv() 

# 로드된 환경 변수 사용
CONNECTION_STRING = os.getenv("CONNECTION_STRING")

# DB 연결 시도
def db_connect():
    client = None
    try:
        client = pymongo.MongoClient(CONNECTION_STRING) 
    except Exception:
        print("Error:", Exception)
    return client