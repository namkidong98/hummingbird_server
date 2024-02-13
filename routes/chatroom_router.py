from fastapi import APIRouter, HTTPException

import sys, json
sys.path.append('../')
from CRUD.user_crud import get_user
from CRUD.chatroom_crud import get_chatroom_by_user, create_chatroom, get_chatroom_by_id
from CRUD.message_crud import get_message
from database import db_connect

router = APIRouter(
    prefix = "/api/user/chatroom",
)

# MongoDB 연결
client = db_connect()


# 친구 목록에서 특정 친구를 누르면 둘 만의 ChatRoom으로 넘어가는 API
@router.get("/") # , response_model=ChatRoom
async def move_chatroom(user_id : str, friend_id : str):
    user = get_user(user_id=user_id, client=client)
    friend = get_user(user_id=friend_id, client=client)
    if not user or not friend: # user_id나 friend_id로 조회되지 않으면
        raise HTTPException(status_code=404, detail="User Not Found") # '응답 없음'을 출력
    
    chatroom = get_chatroom_by_user(user_id=user_id, friend_id=friend_id, client=client)
    if not chatroom: # 기존에 만들어진 채팅방이 없으면 새로 만듦
        chatroom_id = create_chatroom(user_id=user_id, friend_id=friend_id, client=client)
        chatroom = get_chatroom_by_id(chatroom_id=chatroom_id, client=client)
    return json.loads(json.dumps(chatroom, default=str))  # 채팅방을 반환


# 채팅방 내의 누적된 Message를 뒤에서부터 limit개만큼 가져오기
@router.get("/log")
async def getMessageList(chatroom_id : str, limit : int = 1): # limit는 끝에서 몇 개 가져올지
    chatroom = get_chatroom_by_id(chatroom_id=chatroom_id, client=client)
    if not chatroom:
        raise HTTPException(status_code=404, detail="ChatRoom Not Found") # '응답 없음'을 출력
    
    dialogue = chatroom['dialogue'][-limit:] # 채팅방의 Message를 모은 리스트를 뒤에서부터 limit개만큼 가져오기
    result = []
    for message_id in dialogue:
        message = get_message(message_id=message_id, client=client)
        result.append(json.loads(json.dumps(message, default=str)))
    return result