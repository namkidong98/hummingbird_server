from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from functools import partial

import sys, base64, re
sys.path.append('../')
from schema.schema import TaskStatusEnum
from crud.message_crud import create_message, get_message
from crud.chatroom_crud import get_chatroom_by_id, update_dialogue, update_summary

from chat_hummingbird.chatbot import Chatbot
from FlyAIVoice.VoiceModule import TTS

DB_NAME = 'hummingbird'

# 기존에 존재하는 task를 검색(조회)
def get_existing_task(task_id : str, client : MongoClient):
    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})   # 고유 ID로 message를 찾음
    return task

# 새로운 Task 만들기(반환되는 task_id를 Front에서 status를 체크할 때 사용)
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

# Voice 요청 시 Voice_Id를 받아서 DB에서 꺼낸 후 base64 디코딩 후 이진 파일로 반환
def send_binary_voice(voice_id : str, client : MongoClient):
    voice_db = client[DB_NAME]["Voice"]
    voice = voice_db.find_one({"_id" : ObjectId(voice_id)}) # base64로 인코딩되어 있는 문자열 상태
    binary_data = base64.b64decode(voice['audio'])
    return binary_data

# Voice 생성 모델에서 받은 이진 파일로 Voice 객체를 만들어서 DB에 저장
def create_new_voice(task_id : str, audio : bytes, client: MongoClient):
    voice_db = client[DB_NAME]["Voice"]
    task_db = client[DB_NAME]["Task"]

    # 이진 음성 데이터를 Voice로 만들고
    new_voice = {
        "audio" : base64.b64encode(audio).decode("utf-8"), # base64로 인코딩한 데이터가 저장됨
    }
    new_voice_id = voice_db.insert_one(new_voice).inserted_id # DB에 넣고 id를 저장

    # Task의 Voice 리스트에 생성된 Voice의 id를 추가
    task_db.update_one({"_id": ObjectId(task_id)}, {"$push": {"voice": str(new_voice_id)}})    

# Voice 생성 모델(Input : 생성된 텍스트 / Output : 텍스트로 생성한 음성의 bytes)
def voice_model(tts : TTS, sentence : str):
    # sentence를 generate할 문자로 넣기 전에 전처리(문장 끝나기 전에 공백 2칸 추가)
    sentence = sentence.strip()
    text = sentence[:-1] + (sentence[-1] * 3)
    audio_bytes = tts.generate(text=text)
    return audio_bytes

def preprocessing_sentence(sentence : str):
    pattern1 = re.compile(r'[가-힣]{3}:')
    pattern2 = re.compile(r"[가-힣]{3} :")
    pattern3 = re.compile(r"바라")
    new_sentence = re.sub(pattern1, "", sentence)
    new_sentence = re.sub(pattern2, "", new_sentence)
    new_sentence = re.sub(pattern3, "바래", new_sentence)
    return new_sentence

# 한 문장 생성될 때마다 호출
def on_llm_new_sentence_handler(sentence, task_id : str, client : MongoClient, tts : TTS): 
    print(f"setence compelete! : {sentence}")

    task_db = client[DB_NAME]["Task"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})

    # 초기 상태이면, Task의 Status를 doing으로 변경
    if task['task_status'] == "todo": 
        update_task_status(task_id=task_id, status=TaskStatusEnum.doing, client=client) 
    
    sentence = preprocessing_sentence(sentence=sentence)
    # 생성된 응답을 DB(Task)에 저장
    add_answer(task_id=task_id, new_answer=sentence, client=client)

    # 생성된 응답을 음성 모델에 보내서 이진 파일로 받아옴
    binary_audio = voice_model(tts=tts, sentence=sentence)
    
    # 받아온 이진 파일도 DB(Task)에 저장
    create_new_voice(task_id=task_id, audio=binary_audio, client=client)


# 문장 생성이 모두 끝났을 때 호출
def on_llm_end_handler(result, task_id : str, chatroom_id : str, client : MongoClient): 
    print(f"generation complete! : {result}")

    update_task_status(task_id=task_id, status=TaskStatusEnum.done, client=client) # done으로 바꾸고
    message_id = create_message(task_id=task_id, client=client)                    # 완성된 task의 정보를 기반으로 새로운 Message 만들기
    update_dialogue(chatroom_id=chatroom_id, message_id=message_id, client=client) # 새로운 Message의 ID를 dialogue에 추가

# 비동기 함수로 설정
def start_chatbot(friend_id : str, task_id : str,
                  client : MongoClient, chatbot : Chatbot, tts : TTS):
    task_db = client[DB_NAME]["Task"]
    user_db = client[DB_NAME]["User"]
    task = task_db.find_one({"_id" : ObjectId(task_id)})
    chatroom = get_chatroom_by_id(chatroom_id=task['chatroom_id'], client=client)

    user_name = user_db.find_one({"_id" : ObjectId(chatroom['user_id'])})['name']
    ai_name = user_db.find_one({"_id" : ObjectId(chatroom['friend_id'])})['name']

    dialogue = chatroom['dialogue'][-6:]
    
    # 이전 6개까지의 대화 목록 내용을 가져와서 history로 구성
    history = []
    for message_id in dialogue:
        message = get_message(message_id=message_id, client=client)
        answer_sentence = ""
        for ans in message['answer']:
            answer_sentence += ans + " "
        history.append((message['query'], answer_sentence))

    new_sentence_handler = partial(on_llm_new_sentence_handler,
                                          task_id=task_id, client=client, tts=tts)
    end_handler = partial(on_llm_end_handler,
                                 task_id=task_id, chatroom_id=task['chatroom_id'], client = client)

    print(f"Summary Used : {chatroom['summary']}")
    generated, new_summary = chatbot.generate(
        user_name = user_name,
        ai_name = ai_name,
        query = task['query'],  # 새로운 Task에서 들어온 발화
        user_id = friend_id,    # 발화에 대답할 친구의 ID
        relation="우리 딸",
        summary = chatroom['summary'],         # 그동안 나눈 대화의 summary(기존 summary)
        history = history,
        on_llm_new_sentence_handler = new_sentence_handler, # 문장 생성될 때마다 호출되는 함수
        on_llm_end_handler = end_handler,                   # 문장 생성 끝날 때 호출되는 함수
    )

    # summary 추가하는 부분 -> 생성된 Message의 id를 chatroom의 dialogue에 저장
    print(f"summarizing complete! : {new_summary}")
    update_summary(chatroom_id=task['chatroom_id'], client=client, summary=new_summary)  
