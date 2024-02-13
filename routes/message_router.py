from fastapi import APIRouter, HTTPException
from starlette import status

import sys, json
sys.path.append('../')
from database.database import db_connect
from schema.schema import Message
from crud.message_crud import get_message
from crud.chatroom_crud import get_chatroom_by_id

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