import sys, json
sys.path.append('../')
from schema.schema import Task, TaskStatusEnum
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

DB_NAME = 'hummingbird'

# 기존에 존재하는 task를 검색(조회)
def get_existing_task(task_id : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})   # 고유 ID로 message를 찾음
    return task

# 새로운 Task 만들기
def create_new_task(chatroom_id : str, query : str, client: MongoClient):
    task_db = client[DB_NAME]["Task"]
    new_task = {
        "chatroom_id" : chatroom_id,            # 누구끼리의 대화인지 알기 위해
        "task_status" : TaskStatusEnum.todo,    # task의 초기 상태
        "query" : query,                        # 사용자의 발화(input)
        "answer" : [],                          # 생성된 응답을 저장하기 위한 빈 리스트
        "voice" : [],                           # 응답에 따른 음성 파일(binary)을 저장하기 위한 빈 리스트
        "date" : datetime.now()                 # 발화가 들어온 로컬 시간
    }
    new_task_id = task_db.insert_one(new_task).inserted_id
    return json.loads(json.dumps(new_task_id, default=str))

# (new_answer 입력이 없어지고 chatgpt API로 생성하는 모듈이 추가될 예정)
# 새로운 응답이 생성되면 task의 answer 리스트에 추가
def add_answer(task_id : str, new_answer : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task_db.update_one({"_id": ObjectId(task_id)}, {"$push": {"answer": new_answer}})

# DB 안의 Task의 status를 수정
def update_task_status(task_id : str, status : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task_db.update_one({"_id": ObjectId(task_id)}, {"$set": {"task_status": status}})

# # Task의 answer 리스트 안에 응답 추가하기
# def AnswertoTask(chatroom_id : str, task_id : str, new_answer : str, finish: bool = False):
#     task = get_existing_task(answer.task_id, client=client)   # 고유 ID로 task 조회
#     if not task:
#         raise HTTPException(status_code=404, detail="Task Not Found") # '응답 없음'을 출력
    
#     # 상태를 확인하고 필요하면 변경
#     if task['task_status'] == "todo": # 초기 상태이면,
#         update_task_status(task_id=task_id, status=TaskStatusEnum.doing, client=client) # doing으로 변경
#     add_answer(task_id=task_id, new_answer=new_answer, client=client)

#     if answer.finish:  # 만약, 마지막 answer 문장이었다면
#         update_task_status(task_id=answer.task_id, status=TaskStatusEnum.done, client=client) # done으로 바꾸고
#         message_id = create_message(task_id=answer.task_id, client=client) # 완성된 task의 정보를 기반으로 새로운 Message 만들기
#         update_dialogue(chatroom_id=answer.chatroom_id, message_id=message_id, client=client) # 생성된 Message의 id를 chatroom의 dialogue에 저장