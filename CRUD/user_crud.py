import sys
sys.path.append('../')
from schema.schema import User, UserCreate
from pymongo import MongoClient
import json
from bson import ObjectId

DB_NAME = 'hummingbird'

# User 리스트 가져오기
def get_user_list(client : MongoClient):
    db = client[DB_NAME]["User"]
    user_list = []
    for doc in db.find():
        user_list.append(json.loads(json.dumps(doc, default=str)))
    return user_list

# User 생성하기
def create_user(user_create : UserCreate, client : MongoClient):
    db = client[DB_NAME]["User"]
    new_user = {   # UserCreate 부분은 그대로 설정, 나머지는 초기 값으로 설정
        "name": user_create.name,
        "birth" : user_create.birth,
        "sex" : user_create.sex,
        "phone": user_create.phone,
        "friend" : [],
        "voice" : None,
        "persona" : [],
    }
    db.insert_one(new_user)

# 기존의 유저가 있는지 검사
def get_existing_user(user : UserCreate, client : MongoClient):
    db = client[DB_NAME]["User"]
    return db.find_one({'name' : user.name,   # 동일한 이름
                        'birth': user.birth}) # 동일한 생년월일을 가진 document를 반환(없으면 None)

# user_id를 받아서 User 조회
def get_user(user_id : str, client : MongoClient):
    db = client[DB_NAME]["User"]
    user = db.find_one({"_id" : ObjectId(user_id)})
    return user

# User 수정하기(str으로 된 name, phone만 일단 수정 가능)
def update_user(user : User, client : MongoClient, field_name : str, content : str):
    db = client[DB_NAME]["User"]
    query = {"_id" : user['_id']}                      # 찾는 조건
    update_data = {"$set" : {field_name : content}}    # 수정할 내용
    db.update_one(query, update_data)

# User 삭제하기
def drop_user(client : MongoClient, all : bool, name : str, phone : str):
    db = client[DB_NAME]["User"]
    query = {"name" : name, "phone" : phone}
    if all :
        db.delete_many({})    # all=True이면 name, phone가 무관하게 DB에 User 모두 삭제
    else:
        db.delete_one(query)

