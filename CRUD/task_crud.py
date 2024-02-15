from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
from functools import partial

import sys, os, json, asyncio
sys.path.append('../')
from schema.schema import Task, TaskStatusEnum
from crud.message_crud import create_message
from crud.chatroom_crud import get_chatroom_by_id, update_dialogue, update_summary

from chat_hummingbird.chatbot import Chatbot
from chat_hummingbird.generator.openai import OpenAIGenerator
from chat_hummingbird.summarizer.summarizer import Summarizer
from chat_hummingbird.vectordb.chroma_manager import ChromaManager

load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
GENERATOR_MODEL = os.getenv("GENERATOR_MODEL")
SUMMARIZER_MODEL = os.getenv("SUMMARIZER_MODEL") 

DB_NAME = 'hummingbird'

# 기존에 존재하는 task를 검색(조회)
def get_existing_task(task_id : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})   # 고유 ID로 message를 찾음
    return task

# 새로운 Task 만들기(반환되는 task_id를 Front에서 status를 체크할 때 사용)
def create_new_task(chatroom_id : str, query : str, client: MongoClient, manager : ChromaManager):
    task_db = client[DB_NAME]["Task"]
    new_task = {
        "chatroom_id" : chatroom_id,            # 누구끼리의 대화인지 알기 위해
        "task_status" : TaskStatusEnum.todo,    # task의 초기 상태
        "query" : query,                        # 사용자의 발화(input)
        "answer" : [],                          # 생성된 응답을 저장하기 위한 빈 리스트
        "voice" : [],                           # 응답에 따른 음성 파일(binary)을 저장하기 위한 빈 리스트
        "date" : datetime.now()                 # 발화가 들어온 로컬 시간
    }
    new_task_id = task_db.insert_one(new_task).inserted_id # DB에 넣고 id를 저장
    
    chatroom = get_chatroom_by_id(chatroom_id=chatroom_id, client=client) # chatroom_id로 chatroom을 가져오고
    friend_id = chatroom['friend_id']                         # friend_id를 뽑아서

    return str(new_task_id), friend_id                     

# 새로운 응답이 생성되면 task의 answer 리스트에 추가
def add_answer(task_id : str, new_answer : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task_db.update_one({"_id": ObjectId(task_id)}, {"$push": {"answer": new_answer}})

# DB 안의 Task의 status를 수정
def update_task_status(task_id : str, status : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task_db.update_one({"_id": ObjectId(task_id)}, {"$set": {"task_status": status}})

# 한 문장 생성될 때마다 호출
def on_llm_new_sentence_handler(sentence, task_id : str, client : MongoClient): 
    print(f"setence compelete! : {sentence}")
    # 상태를 확인하고 필요하면 변경
    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})
    if task['task_status'] == "todo": # 초기 상태이면,
        update_task_status(task_id=task_id, status=TaskStatusEnum.doing, client=client) # doing으로 변경
    add_answer(task_id=task_id, new_answer=sentence, client=client)

# 문장 생성이 모두 끝났을 때 호출
def on_llm_end_handler(result, task_id : str, chatroom_id : str, client : MongoClient): 
    print(f"generation complete! : {result}")
    update_task_status(task_id=task_id, status=TaskStatusEnum.done, client=client) # done으로 바꾸고
    message_id = create_message(task_id=task_id, client=client)                    # 완성된 task의 정보를 기반으로 새로운 Message 만들기
    update_dialogue(chatroom_id=chatroom_id, message_id=message_id, client=client) # 새로운 Message의 ID를 dialogue에 추가
    

# 비동기 함수로 설정
async def start_chatbot(friend_id : str, task_id : str, client : MongoClient, manager : ChromaManager):
    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})
    chatroom = get_chatroom_by_id(chatroom_id=task['chatroom_id'], client=client)
    
    # 이 부분을 main에서 맨 처음 호출하고 request로 넘겨줘야 할까? (resource 낭비?)
    generator = OpenAIGenerator(model_name=GENERATOR_MODEL, openai_api_key=OPENAI_API_KEY)
    summarizer = Summarizer(model_name=SUMMARIZER_MODEL)
    chatbot = Chatbot(generator=generator, summarizor=summarizer, db_manager=manager)

    new_sentence_handler = partial(on_llm_new_sentence_handler,
                                          task_id=task_id, client=client)
    end_handler = partial(on_llm_end_handler,
                                 task_id=task_id, chatroom_id=task['chatroom_id'], client = client)

    print(f"Summary Used : {chatroom['summary']}")
    generated, new_summary = chatbot.generate(
        query = task['query'],  # 새로운 Task에서 들어온 발화
        user_id = friend_id,    # 발화에 대답할 친구의 ID
        summary = chatroom['summary'],         # 그동안 나눈 대화의 summary(기존 summary)
        on_llm_new_sentence_handler = new_sentence_handler, # 문장 생성될 때마다 호출되는 함수
        on_llm_end_handler = end_handler,                   # 문장 생성 끝날 때 호출되는 함수
    )

    # summary 추가하는 부분 -> 생성된 Message의 id를 chatroom의 dialogue에 저장
    print(f"summarizing complete! : {new_summary}")
    update_summary(chatroom_id=task['chatroom_id'], client=client, summary=new_summary) 