from fastapi import APIRouter, HTTPException, Depends, Request
from starlette import status

import sys, asyncio
sys.path.append('../')
from schema.schema import Task, TaskStatusEnum, TaskCreate
from crud.task_crud import get_existing_task, create_new_task, start_chatbot

router = APIRouter(
    prefix = "/api/user/task",
)

# 어떤 채팅방(chatroom_id)에서 나온 발화(query)인지를 받아서 Task 만들기(Front와 통신)
@router.post("/create")
async def createTask(request : Request, task: TaskCreate):
    task_id, friend_id = create_new_task(chatroom_id=task.chatroom_id, query=task.query,
                              client=request.app.client, manager=request.app.manager)
    
    # start_chatbot을 백그라운드에서 실행
    asyncio.create_task(start_chatbot(friend_id=friend_id, task_id=task_id,
                                      client=request.app.client, manager=request.app.manager,
                                      ))
    return task_id

# 생성된 task의 id를 지속적으로 보내면서 상태를 확인(Front와 통신)
@router.get("/status")
async def getTaskStatus(request : Request, task_id : str):
    task = get_existing_task(task_id, client=request.app.client)
    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found") # '응답 없음'을 출력
    return {"task_status" : task['task_status'], "len" : len(task['answer'])}


# 음성(지금은 텍스트) 요청하면 주는 API(Front와 통신)
@router.get("/answer")
async def sendAnswer(request : Request, task_id : str, index : int):
    task = get_existing_task(task_id, client=request.app.client)
    if not task: # 해당하는 Task가 없으면
        raise HTTPException(status_code=404, detail="Task Not Found") # '응답 없음'을 출력
    if (index-1 >= len(task['answer'])) or (index <= 0): # 잘못된 index 값이 들어오면
        raise HTTPException(status_code=404, detail="Invalid Index for Answer")
    return task['answer'][index-1]
