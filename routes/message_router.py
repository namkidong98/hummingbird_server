from fastapi import APIRouter, HTTPException
from starlette import status

import sys, json
sys.path.append('../')
from database import db_connect
from schemas.schema import Message
from CRUD.message_crud import get_message
from CRUD.chatroom_crud import get_chatroom_by_id

router = APIRouter(
    prefix = "/api/user/message",
)

# MongoDB 연결
client = db_connect()

# message_id로 
@router.get("/")
async def getMessage(message_id : str):
    message = get_message(message_id=message_id, client=client)
    return json.loads(json.dumps(message, default=str))