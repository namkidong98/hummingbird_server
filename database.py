import os, sys
from dotenv import load_dotenv 
import pymongo
# from fastapi.encoders import jsonable_encoder

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

# client = db_connect()
# db = client['hummingbird']['User']

# print([i for i in db.find()])

# print(db.find_one({'phone' : '010-2761-3934',
#                    'name'  : 'kidong'}))

# if db:
#     # DB 접근
#     DB_NAME = "hummingbird"
#     db = client[DB_NAME]    
#     if DB_NAME not in client.list_database_names():
#         db.command({"customAction" : "CreateDatabase"})
#         print("Created DB : '{}'".format(DB_NAME))
#     else:
#         print("DB in Use: '{}'".format(DB_NAME))

#     # Collection 접근
#     COLLECTION_NAME = 'User'
#     collection = db[COLLECTION_NAME]    
#     if COLLECTION_NAME not in db.list_collection_names():
#         db.command(
#             {"customAction" : "CreateCollection", "collection" : COLLECTION_NAME}
#         )
#         print("Created Collection : '{}'\n".format(COLLECTION_NAME))
#     else:
#         print("Collection in Use : '{}'\n".format(COLLECTION_NAME))

    # new = {
    #     "name" : "jeon",
    #     "phone" : "010-2222-2222",
    #     "friend" : ["song", "kim", "kidong", "hwang"]
    # }

    # collection.insert_one(new).inserted_id

#     for doc in collection.find():
#         print(doc)

# client.close()