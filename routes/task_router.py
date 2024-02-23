from fastapi import APIRouter, HTTPException, Request, BackgroundTasks, Response
from starlette import status

import sys
sys.path.append('../')
from schema.schema import TaskCreate
from crud.task_crud import get_existing_task, create_new_task, start_chatbot, send_binary_voice

router = APIRouter(
    prefix = "/api/user/task",
)

# 어떤 채팅방(chatroom_id)에서 나온 발화(query)인지를 받아서 Task 만들기(Front와 통신)
@router.post("/create")
async def createTask(request : Request, task: TaskCreate, background_tasks: BackgroundTasks):
    task_id, friend_id = create_new_task(chatroom_id=task.chatroom_id, query=task.query,
                              client=request.app.client)
    
    # start_chatbot을 백그라운드에서 실행
    background_tasks.add_task(start_chatbot,
                              friend_id=friend_id, task_id=task_id,
                              client=request.app.client, chatbot=request.app.chatbot) # 
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
    
    # voice 생성까지 대기
    while len(task['voice']) <= index-1:
        pass
    voice_id = task['voice'][index-1]
    
    # voice_id로 DB에서 binary file을 가져오는 함수 --> 가져온 binary file을 return
    binary_data = send_binary_voice(voice_id=voice_id, client=request.app.client)
    return Response(content=binary_data, media_type="audio/wav")