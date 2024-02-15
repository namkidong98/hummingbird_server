import sys, json
sys.path.append('../')
from schema.schema import Task, TaskStatusEnum

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

DB_NAME = 'hummingbird'

# Task가 끝나면("done") Task의 정보로 Message를 만들고 만들어진 Message의 id를 반환
def create_message(task_id : str, client : MongoClient):
    message_db = client[DB_NAME]["Message"]
    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})
    # task = get_existing_task(task_id=task_id, client=client) # task_id로 task 가져오고
    # task의 정보를 바탕으로 Message 만들기
    new_message = {
        "query" : task['query'],
        "answer" : task['answer'],
        "date" : task['date']
    }
    new_message_id = message_db.insert_one(new_message).inserted_id # DB에 저장하고 id를 반환
    return json.loads(json.dumps(new_message_id, default=str))

def get_message(message_id : str, client : MongoClient):
    message_db = client[DB_NAME]["Message"]
    message = message_db.find_one({"_id" : ObjectId(message_id)})
    return message

