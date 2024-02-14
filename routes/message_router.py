from fastapi import APIRouter, HTTPException, Depends, Request
from pymongo import MongoClient
from starlette import status

import sys, json
sys.path.append('../')
from schema.schema import Message
from crud.message_crud import get_message
from crud.chatroom_crud import get_chatroom_by_id

router = APIRouter(
    prefix = "/api/user/message",
)

# message_id로 
@router.get("/")
async def getMessage(request : Request, message_id : str):
    message = get_message(message_id=message_id, client=request.app.client)
    return json.loads(json.dumps(message, default=str))