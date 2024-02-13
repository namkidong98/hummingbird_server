import sys, json
sys.path.append('../')
from schema.schema import ChatRoom

from pymongo import MongoClient
from bson import ObjectId

DB_NAME = 'hummingbird'

# chatroom_id로 ChatRoom을 조회 및 반환
def get_chatroom_by_id(chatroom_id : str, client : MongoClient):
    chatroom_db = client[DB_NAME]["ChatRoom"]
    chatroom = chatroom_db.find_one({"_id" : ObjectId(chatroom_id)})
    return chatroom

# user_id와 friend_id로 ChatRoom을 조회
def get_chatroom_by_user(user_id : str, friend_id : str, client : MongoClient):
    chatroom_db = client[DB_NAME]["ChatRoom"]
    chatroom = chatroom_db.find_one({"user_id": user_id, "friend_id": friend_id})
    return chatroom

# user와 friend 사이의 chatroom이 없을 때 새로 만들어서 id를 반환
def create_chatroom(user_id : str, friend_id : str, client : MongoClient):
    chatroom_db = client[DB_NAME]["ChatRoom"]
    new_chatroom = {
        "user_id" : user_id,
        "friend_id" : friend_id,
        "dialogue" : [],     # message 저장할 공간은 빈 리스트로 초기 설정
        "summary" : ""       # 일단 빈 문자열로 초기 설정
    }
    new_chatroom_id = chatroom_db.insert_one(new_chatroom).inserted_id
    return json.loads(json.dumps(new_chatroom_id, default=str))

# 만들어진 Message의 id를 해당된 chatroom의 dialogue에 추가
def update_dialogue(chatroom_id : str, message_id : str, client : MongoClient):
    chatroom_db = client[DB_NAME]["ChatRoom"]
    chatroom_db.update_one({"_id": ObjectId(chatroom_id)}, {"$push": {"dialogue": message_id}})


