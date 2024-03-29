import sys, json
sys.path.append('../')
from schema.schema import User, UserCreate
from pymongo import MongoClient
from chat_hummingbird.vectordb.chroma_manager import ChromaManager
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
        "persona" : {},
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

# User 페르소나 불러오기
def get_persona(user_id : str, client : MongoClient):
    db = client[DB_NAME]["User"]
    user = db.find_one({"_id" : ObjectId(user_id)})
    return json.loads(json.dumps(user['persona'], default=str))


# User 페르소나 추가하기
def add_persona(user_id : str, title : str, content : str, client : MongoClient, manager : ChromaManager):
    db = client[DB_NAME]["User"]    # MongoDB

    # Mongo DB에 persona(딕셔너리)에 추가 or 업데이트
    key = "persona." + title
    db.update_one({"_id": ObjectId(user_id)}, {"$set": {key: content}})

    # Chroma DB에 persona 제거하고 다시 추가하기
    user = db.find_one({"_id" : ObjectId(user_id)}) # 수정된 이후의 정보로 가져옴
    manager.delete_personas_by_user_id(user_id=user_id) # Chroma 내 기존의 페르소나는 지우고
    script = ""
    for key, value in user['persona'].items():
        script += (key + "에는 " + value + " ")
    result = manager.add_persona(persona=script, user_id=user_id) # MongoDB의 페르소나를 합쳐서 Chroma에 추가
    
    
        

    
