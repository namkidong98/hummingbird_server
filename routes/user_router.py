from fastapi import APIRouter, HTTPException, Request
from starlette import status
from typing import Optional

import sys, json
sys.path.append('../')
from schema.schema import User, UserCreate, UpdatePersona
from crud.user_crud import (get_user_list, create_user,
                            get_existing_user, update_user,
                            drop_user, get_user, add_persona)

router = APIRouter(
    prefix = "/api/user",
)

# User 리스트 조회
@router.get("/list")
async def user_list(request : Request):
    return get_user_list(client=request.app.client)

# User 생성
@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
async def user_create(request : Request, _user_create : UserCreate):
    user = get_existing_user(user = _user_create, client=request.app.client)  # 우선 기존 유저가 있는지 검사하고
    if user:    # 기존 유저가 있으면
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,   # 에러 메시지 출력
                            detail="이미 존재하는 사용자입니다")
    create_user(user_create= _user_create, client=request.app.client)       # 기존 유저가 없으면 DB에 추가


# # User 수정
# @router.post("/update", status_code=status.HTTP_204_NO_CONTENT)
# async def user_update(request : Request, existing_user : User, field_name : str, content : str):
#     user = get_existing_user(user = existing_user, client=request.app.client)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT,   # 에러 메시지 출력
#                             detail="존재하지 않는 사용자입니다")
#     update_user(user=user, client=request.app.client, field_name=field_name, content=content)


# User 삭제
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(request : Request, all : bool, name : Optional[str] = None, phone : Optional[str] = None):
    drop_user(client=request.app.client, all=all, name=name, phone=phone)


# 등록된 친구 목록을 나타내기 위한 API(2번째 카테고리의 메인)
@router.get("/friend_list") # , response_model=list[User]
async def get_friend_list(request : Request, user_id : str):
    user = get_user(user_id=user_id, client=request.app.client)
    if not user: # 해당 ID의 유저가 없으면
        raise HTTPException(status_code=404, detail="User Not Found") # '응답 없음'을 출력
    
    friend_list = user['friend']    # 해당 유저의 friend_id가 저장된 리스트
    result = []
    for friend_id in friend_list:
        doc = get_user(user_id=friend_id, client=request.app.client)  # 각각의 id로 조회한 document를
        result.append(json.loads(json.dumps(doc, default=str))) # json 형식으로 변환해서 리스트에 추가
    return sorted(result, key=lambda x: x['name'])  # 각각의 User 데이터의 이름(name) 순서로 정렬해서 반환

# Persona 수정하기
@router.post("/persona")
async def user_update(request : Request, update_persona : UpdatePersona):
    user = get_user(user_id = update_persona.user_id, client=request.app.client)
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,   # 에러 메시지 출력
                            detail="존재하지 않는 사용자입니다")
    add_persona(user_id=update_persona.user_id, title=update_persona.title, content=update_persona.content,
                client=request.app.client, manager=request.app.manager)