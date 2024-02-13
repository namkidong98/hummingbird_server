from pydantic import BaseModel, Field
import datetime
from enum import Enum
from typing import Literal

class QnA(BaseModel):   # 페르소나에 사용되는 질문-대답 묶음
    question : str      # 페르소나 질문
    answer : str        # 페르소나 질문에 대한 응답

class Message(BaseModel):       # 채팅방의 발화-응답 묶음(Task가 끝나면 만듦)
    _id : str  
    query : str                 # 발화
    answer : list[str]          # 발화에 대한 응답
    date : datetime.datetime    # 발화가 된 시간

class Voice(BaseModel): # 페르소나를 위한 개인 음성, 대화에서 생성된 음성 등 모든 음성들에 대한 스키마
    _id : str
    audio : bytes       # Binary로 변환된 음성 데이터(인코딩)

class TaskStatusEnum(str, Enum):
    todo = "todo"       # task가 생성되었을 때 초기값
    doing = "doing"     # task가 응답을 생성하는 중
    done = "done"       # task가 응답을 모두 생성한 이후

class Task(BaseModel):          # 발화에 대해 생성된 응답, 합성된 음성 묶음
    _id : str 
    chatroom_id : str   
    task_status : TaskStatusEnum # task의 상태를 나타냄
    query : str | None = None   # 사용자의 발화
    answer : list[str] = []     # 발화에 대한 응답이 생길 때마다 문장 단위로 저장
    date  :datetime.datetime    # query가 들어온 시간
    voice : list[str] = []      # 생성된 voice들의 id를 저장

class User(BaseModel):
    _id : str
    name : str = Field(..., min_length=2, max_length=4, example="남기동")
    birth : str = Field(..., min_length=6, max_length=6, example="981229")
    sex : Literal["male", "female"]
    phone: str = Field(..., regex=r'^010-[0-9]{3,4}-[0-9]{4}$', example="010-2761-3934")
    friend : list[str] = []      # user_id의 리스트
    voice : Voice | None = None  # 유저가 저장한 본인 목소리
    persona : list[QnA] = []     # 유저의 페르소나 생성에 사용된 응답 모음

class ChatRoom(BaseModel):
    _id : str
    user_id : str               # 사용자의 _id만
    friend_id : str             # 사용자의 친구 목록 중 한 명의 _id만
    dialogue : list[str] = []   # Message의 _id들만 저장
    summary : str | None = None # 처음에는 빈 문자열이고 Message 누적될 때마다 Summary도 갱신