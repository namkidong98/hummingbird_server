from fastapi import APIRouter, HTTPException
from starlette import status

import sys
sys.path.append('../')
from database.database import db_connect
from schema.schema import TaskStatusEnum
from crud.task_crud import (get_existing_task, create_new_task, add_answer, update_task_status,)
from crud.message_crud import create_message
from crud.chatroom_crud import update_dialogue

router = APIRouter(
    prefix = "/api/user/task",
)

# MongoDB 연결
client = db_connect()


# 어떤 채팅방(chatroom_id)에서 나온 발화(query)인지를 받아서 Task 만들기(Front와 통신)
@router.post("/create")
async def createTask(chatroom_id : str, query : str):
    task_id = create_new_task(chatroom_id=chatroom_id, query=query, client=client)
    return task_id


# Task의 answer 리스트 안에 응답 추가하기
@router.post("/answer")
async def addAnswer(chatroom_id : str, task_id : str, new_answer : str, finish : bool):    # finish는 마지막 answer인지를 의미
    task = get_existing_task(task_id, client=client)   # 고유 ID로 task 조회
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found") # '응답 없음'을 출력
    
    # 상태를 확인하고 필요하면 변경
    if task['task_status'] == "todo": # 초기 상태이면,
        update_task_status(task_id=task_id, status=TaskStatusEnum.doing, client=client) # doing으로 변경
    add_answer(task_id=task_id, new_answer=new_answer, client=client)

    if finish:  # 만약, 마지막 answer 문장이었다면
        update_task_status(task_id=task_id, status=TaskStatusEnum.done, client=client) # done으로 바꾸고
        message_id = create_message(task_id=task_id, client=client) # 완성된 task의 정보를 기반으로 새로운 Message 만들기
        update_dialogue(chatroom_id=chatroom_id, message_id=message_id, client=client) # 생성된 Message의 id를 chatroom의 dialogue에 저장


# 생성된 task의 id를 지속적으로 보내면서 상태를 확인(Front와 통신)
@router.get("/status")
async def getTaskStatus(task_id : str):
    task = get_existing_task(task_id, client=client)
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found") # '응답 없음'을 출력
    return {"task_status" : task['task_status'], "len" : len(task['answer'])}


# 음성(지금은 텍스트) 요청하면 주는 API(Front와 통신)
@router.get("/answer")
async def sendAnswer(task_id : str, index : int):
    task = get_existing_task(task_id, client=client)
    if not task: # 해당하는 Task가 없으면
        raise HTTPException(status_code=404, detail="Task Not Found") # '응답 없음'을 출력
    if (index-1 > len(task['answer'])) or (index <= 0): # 잘못된 index 값이 들어오면
        raise HTTPException(status_code=404, detail="Invalid Index for Answer")
    return task['answer'][index-1]