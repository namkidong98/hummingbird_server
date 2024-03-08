# Hummingbird Server

<img width=800 src="https://github.com/namkidong98/hummingbird_server/assets/113520117/d693ae86-a0d7-4e90-b25a-f4a590e28620">

- 프로젝트명 : HummingBird    
- 프로젝트 목표 : Well-Dying을 위해 자신의 페르소나와 목소리를 학습시켜 자신의 죽음 이후 지인들이 자신과 전화하는 것과 같은 경험을 제공해주는 것을 목표로 한다   
- 프로젝트 기간 : 2024.02.01 ~ 2024.02.28 (1달)
- 프로젝트 인원 : 김세희, 김종수, 남기동, 송성근, 전윤찬, 황승현
- 핵심 담당 업무 : Backend, Cloud

<br>

<img width=800 src="https://github.com/namkidong98/hummingbird_server/assets/113520117/08d3df3d-0eb1-4a7d-b405-23f58c77cdc7">


<br><br>

# 백엔드 작업 요약
1. ChromaDB 연결, MongoDB 연결

2. 채팅 모델을 연결 (Chat-Hummingbird)   
    LangChain과 ChatGPT로 응답을 생성하는 채팅 모델을 서버에 연결   
    ChatGPT를 통해 생성되는 답변을 문장 단위로 가져와 DB에 저장하고 프론트 요청에 따라 반환   
   
3. 음성 모델을 연결   
    VITS 모델을 사용한 TTS(Text to Speech) 모델을 서버에 연결   
    ChatGPT에서 생성된 문장으로 음성을 합성하여 문장 단위의 wav 파일을 binary 형태로 프론트에 전달   
   
4. Docker – ChromaDB, FastAPI 분리하고 컨테이너화
    Docker를 이용하여 DB와 Backend를 분리하고 컨테이너화   
    서버와 DB를 분리하여 서버에 문제가 생기더라도 DB에 피해가 가지 않도록 독립성을 확보   

5. Azure를 이용한 배포   
    MongoDB는 MongoDB Atlas라는 클라우드 서비스로 작동      
    ChromaDB는 ACI(Azure Container Instance)를 이용해 Docker 이미지를 올려서 배포   
    FastAPI는 GPU 리소스를 사용해야 하므로 Azure 구독 업그레이드가 필요하여 로컬에서 열어서 사용   

<br>

# MongoDB

### Pymongo

- Pymongo는 MongoDB와 상호작용하기 위한 Python 라이브러리이다

https://wooiljeong.github.io/python/mongodb-01/      
https://www.youtube.com/watch?v=GJCKIGeK3qc&t=337s   

<br>

### MongoDB Atlas 가입 및 DB 생성

- MongoDB Atlas는 MongoDB의 관리형 클라우드 데이터베이스 서비스로 손쉽게 배포하고 운영할 수 있게 도와준다
- MongoDB Atlas에서는 512MB의 DB를 무료로 이용 가능하게 한다는 장점이 있다(신용 카드도 연결하지 않아 과금에 대한 걱정이 없다)

<br>

<img width="806" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/82a888eb-294b-42fa-8910-17f31a8a39a6">

- 'HummingBird' 프로젝트 생성

<br>

<img width="400" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/28c857a4-babc-44e4-9e36-d09d8b2b416b">
<img width="400" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/57c61da5-4fa4-4776-8da5-4af9883839a8">

- Username과 Password를 설정하고 현재 IP 주소를 추가
- **MongoDB에 접속하는 경우 Connection_String을 사용하게 되는데, Connection_String을 사용하더라도 MongoDB에서 현재 IP가 허용된 IP인지를 체크한다**
- **따라서 접속이 안 되는 경우 MongoDB Atlas에서 "Add Current IP" 옵션을 사용해야 한다**

<br>

<img width="450" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/bbc21149-a027-4280-8dc4-5b5e0275ea64">
<img width="450" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/eb53f41e-28b5-4f79-ad8b-0e7c90769454">
<img width="450" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/80a3bcf6-09f2-42af-a73b-52583d750290">
<img width="450" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/83b14d99-23ef-4a0e-b28f-1d0b2d5db694">

- project를 만들고 connect를 누른 후 MongoDB for VSCode를 눌러 Connection_String을 얻을 수 있다(프로그램 내에서 연결을 위해 사용)
- VSCode에서 Extension을 다운로드 받고 MongoDB를 연결한다(MongoDB Atlas에 접속하지 않고 간단히 VSCode에서 조회할 수 있는 기능을 위해)

<br>

<img width="553" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/56d44f65-9f54-4787-b44b-20c63e4ab5c9">
- 좌측에 MongoDB에서 'cluster0'에 연결되어 Database에 접근할 수 있는 것을 확인할 수 있다
- database.py의 코드에서는 CONNECTION_STRING을 통해 프로그램 내에서 DB에 접근하는 것을 나타내고 있다

<br>

<img width="726" alt="image" src="https://github.com/namkidong98/hummingbird_server/assets/113520117/37b03086-1aaa-4130-9177-bab99aaff121">

- new라는 임의의 데이터를 collection에 insert하기 전과 insert한 이후에 'User' collection 내부의 Documents를 하나씩 출력하여 차이를 확인해볼 수 있었다

<br>

# FastAPI로 BackEnd Application 개발

### 환경 설정 및 필요한 라이브러리 다운로드

```
python -m venv venv      # venv라는 이름의 가상 환경 생성
.\venv\Scripts\activate  # 가상환경 venv 활성화
```

```txt
fastapi
uvicorn[standard]
pydantic
pymongo
python-dotenv
```

```shell
# 위의 내용을 담은 requirements.txt 파일을 생성
pip install -r requirements.txt  # requirements.txt 파일을 읽어서 라이브러리 설치
```

- 가상 환경을 생성 및 활성화하고 requirements.txt 파일을 생성하고 이를 읽어서 라이브러리를 설치하도록 명령어를 실행한다
- 주의할 사항은 vscode의 terminal에서 powershell이 아닌 command prompt로 진행해야 한다는 것이다

<br>

### FastAPI로 생성한 백엔드 어플리케이션 테스트

```python
# main.py 생성
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
def hello():
    return {"message" : "안녕하세요!"}
```

```shell
uvicorn main:app --reload
```

- main.py 파일을 위와 같이 생성한다 (로컬 IP로 연결이 되는지 확인하기 위한 예제로 간단히 작성한 예제 코드이다)
- uvicorn main:app --reload 에서 reload 옵션을 통해 파일이 수정되는 대로 반영되게 한다

<br>

<img width="450" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/f67c73a2-9d6b-401a-b9fc-d43d4e2722e9">
<img width="450" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/6e36d5b7-e280-471b-b690-5f9735e077ee">

- swagger Docs로 간단히 테스트 해볼 수 있으며, 기본적으로 "/hello"에 대한 GET 요청이 제대로 작동하는 것을 확인할 수 있다

<br>

# ChromaDB 연결

### 가상환경 설정

```shell
py -3.9 -m venv .venv        # 원하는 파이썬 버전으로 가상환경 만들기
.venv\Scripts\activate       # 가상환경 활성화
.venv\Scripts\deactivate.bat # 가상환경 비활성화
rmdir /s /q .venv            # 가상환경 삭제
```

- 처음에는 이러한 방식으로 하였는데, Chroma DB부터는 Torch도 사용해야 하기 때문에 conda 가상환경을 설정하고 사용하기로 한다

<br>

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/26a15572-1622-431b-b635-41e776f255e2">
<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/2e9f60b9-a60b-4a27-9870-c1f737992f13">

```shell
conda create -n venv python=3.9  # conda 가상환경 만들기
conda activate venv              # conda 가상환경 활성화
pip install -r requirements.txt  # 로컬의 requirements를 읽어서 다운로드
pip install git+(github주소)@(branch이름)    # chromaDB와 생성형 모델을 위한 설치

chroma run --port 8001 --host localhost    # ChromaDB 실행하기
```

<br>

### CUDA 설치 및 사용

<img width="600" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/e5fd644b-abc8-438b-8caa-0076b7964002">

1. https://developer.nvidia.com/cuda-11-7-0-download-archive 에서 toolkit을 다운로드 한다(너무 최신 버전은 오류가 발생한다)
2. 다운로드 받은 프로그램을 실행하여 CUDA를 설치한다(C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA에서 버전 확인 가능)
3. 터미널에서 torch를 uninstall하고 CUDA 버전에 맞는 torch를 설치할 준비를 한다
4. https://pytorch.org/get-started/locally/ 에서 환경에 따른 설치 명령어를 체크한다(끝에 cu118을 맞는 버전에 맞게 변경한다)

```shell
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117     # CUDA v11.7인 경우

python
>>> import torch
>>> torch.cuda.is_available()

# 위의 파이썬 명령어에 대해 True가 나오면 torch를 쓸 수 있는 상황이다
```

<br>

### FastAPI에서 DB 연결하는 부분

```python
from fastapi import FastAPI
from database.database import db_connect, vector_connect

app = FastAPI()

@app.on_event("startup")
def startup_db_client():
    app.client = db_connect()       # MongoDB 연결
    app.vector = vector_connect()   # ChromaDB 연결(vector search를 위해)

@app.on_event("shutdown")
def shutdown_db_client():
    app.client.close()
```

- app.on_event를 사용하여 처음 fastapi 어플리케이션을 만들었을 때 DB를 연결하고 끝날 때 종료하도록 한다

<br>

```python
from fastapi import APIRouter, HTTPException, Depends, Request

# 어떤 채팅방(chatroom_id)에서 나온 발화(query)인지를 받아서 Task 만들기(Front와 통신)
@router.post("/create")
async def createTask(request : Request, task: TaskCreate):
    task_id = create_new_task(chatroom_id=task.chatroom_id, query=task.query, client=request.app.client)
    return task_id
```

- 이런 방식으로 라우터 파일에서 request:Request, request.app.client로 MongoDB client를 사용할 수 있다

<br>

# 동일 WiFi를 사용하는 팀원과 FastAPI 사용

<img width="500" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/797a2b9b-5ec1-4746-a740-47e40a55337b">
<img width="300" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/1e867799-4819-4f15-8cdd-f40ac3a38a65">

```
uvicorn main:app --reload --host 192.100.01.01
```

- 위와 같이 프롬프트에서 'ipconfig' 명령어를 사용하여 "무선 LAN 어댑터 Wi-Fi"의 IPv4주소로 IP 주소를 확인한다
- uvicorn main:app으로 fastapi를 실행할 때 --host 옵션에 Wi-Fi의 IP주소를 입력한다
- 이렇게 하면 기존의 로컬 환경에서 127.0.0.1:8000으로 연결하면 주소를 IP 주소로 대체하여 동일 Wi-Fi 사용자가 접근할 수 있다

<br>

# 완성된 프로젝트 Docker로 컨테이너화
### 1. ChromaDB

```docker
# syntax=docker/dockerfile:1

# Use the official Python image as the base image
FROM python:3.9 

# Set the working directory in the container
WORKDIR /chroma

# Install dependencies
RUN pip install chromadb

# Expose the port that the app will run on
EXPOSE 8001

# Command to run the application
CMD ["chroma", "run", "--host", "0.0.0.0", "--port", "8001"]
```

```shell
# Docker Desktop 열기
docker build --no-cache -t chromadb .
docker run --name chromadb -p 8001:8001 chromadb
```

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/9650d45c-2014-4b3f-87fc-22e36350040b">

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/eef031e4-de4c-4674-8c03-73a271de70bf">

1. ChromaDB를 분리하기 위한 Dockerfile을 위와 같이 작성한다
2. Docker Desktop을 열고 Dockerfile이 있는 디렉토리에서 터미널을 통해 docker build를 한다   
    cf) --no-cache를 해야 수정되는 사항이 문제 없이 반영될 수 있다
3. docker run으로 ChromaDB를 실행한다

<br>

### 2. Backend Server(FastAPI)

```docker
# syntax=docker/dockerfile:1

# Use the official Python image as the base image
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# Set the working directory in the container
WORKDIR /hummingbird_server

# Git이 설치되어 있는지 확인하고 설치
RUN apt-get update && apt-get install -y git

# Install any dependencies
RUN git clone -b test1 https://github.com/namkidong98/hummingbird_server.git .
RUN cd /hummingbird_server
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/yeti-s/chat-hummingbird.git@dev-prompt-debugger

# Copy the rest of the application code to the working directory
COPY .env .

# Expose the port that the app will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

1. pytorch를 base image로 하며 git clone과 github에서 pip install 하는 부분을 위해 git을 설치한다
2. git clone을 한 이후 'hummingbird_server'라는 폴더가 생기기 때문에 cd 명령어로 디렉토리를 변경해주어야만 한다
3. 로컬에서 모든 파일을 COPY하지 않고 git clone을 하는 이유는 불필요한 파일(ex. pycache)을 제외하고 다운로드 할 수 있기 때문이다
4. "COPY .env ."를 통해 백엔드 서버 작동을 위해 필수적인 환경 변수들을 가져올 수 있도록 한다

<br>

```shell
# Docker Desktop 열기
docker build --no-cache -t hummingbird_server .
docker run --gpus all --name hummingbird_server -p 8000:8000 hummingbird_server
```

<img width="600" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/9e7cdc73-c7d5-432c-b162-cb36527895aa">

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/796b7842-6c76-40fa-b4db-21e127dc6f3c">

1. Dockerfile을 위와 같이 작성하여 FastAPI로 백엔드 서버를 여는 부분을 컨테이너화 한다
2. Docker Desktop을 열고 Dockerfile이 있는 디렉토리에서 터미널을 통해 docker build를 한다   
    cf) --no-cache를 해야 수정되는 사항이 문제 없이 반영될 수 있다(특히나 git을 수정한 경우 캐시 때문에 변경 사항이 반영 안되는 문제가 발생할 수 있다)   
    cf) Dockerfile에서 git clone으로 파일을 로드하면 홈 디렉토리에서 main이 있는 디렉토리로 cd 명령어를 통해 이동해주어야만 한다   
3. docker run으로 백엔드 서버를 실행할 때 "--gpus all" 옵션을 주어 GPU 사용을 가능하게 해주어야 한다   

<br><br>

# Docker를 이용하여 Azure를 통해 배포

<img width="538" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/02b4ea43-a2ee-4eb3-a5c0-9b0854596e3f">

- 리소스 그룹 만들기

<br>

<img width="403" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/4cd6ff7a-987b-4748-a928-e472a2b2ff4c">
<img width="560" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/57ea3fee-10da-41d3-91d8-6f3ac1c8084b">

- 컨테이너 레지스트리(ACR, Azure Container Registry) 만들기

<br>

<img width="515" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/16ef224f-ceb8-4949-8244-b5728a218ed0">

- 컨테이너 레지스트리의 액세스 키에서 "관리 사용자"를 활성화하여 Username과 Password를 확인한다

<br>

<img width="484" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/0e8bae2d-70b2-4abf-9e30-39e6a9f29ae8">

- VSCode에서 '액세스 키'에서 확인한 Username과 Password로 로그인(복사한 password를 붙여 넣을 때 ctrl + shift + v를 해야 한다!)

<br>

<img width="601" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/665920c3-2e78-42dd-aeb9-5981a64eb27a">

```shell
# chromaDB image push
docker tag chromadb hummingbird.azurecr.io/chromadb
docker push hummingbird.azurecr.io/chromadb

# back_server image push
docker tag hummingbird_local hummingbird.azurecr.io/back_server
docker push hummingbird.azurecr.io/back_server

docker images # hummingbird.azurecr.io/chromadb, hummingbird.azurecr.io/back_server이 추가된 것을 확인 가능
```

- docker tag, docker push를 이용하여 ChromaDB와 Back Server 이미지를 Azure의 컨테이너 레지스트리에 올린다

<br>

### 방법1 : Azure에서 직접 만들기

<img width="600" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/3ae13ee0-9efa-455a-be9c-5e8eb8db7592">

- ACI(Azure Container Instance)를 만들고 '이미지 원본'을 ACR(Azure Container Registry)로 하여 push한 이미지를 사용한다

<br>

<img width="600" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/bd9d9a38-9bd7-411c-96ba-c24089e97865">

- ChromaDB는 8001 포트로 연결할 것이기 때문에 8001 포트를 열어 놓는다

<br>

### 방법2 : VSCode에서 docker 명령어로 만들기

```shell
docker login azure                            # docker 로그인
docker context create aci myacicontext        # context 만들기
# resource group 선택하기                      # resource group 선택하여 context 확정
docker context ls                             # context 목록 확인
docker context use myacicontext               # 만들어둔 context 활성화
docker ps                                     # 현재 컨테이너들의 상태를 확인 
docker run --name chromadb -p 8001:8001 hummingbird.azurecr.io/chromadb # 8001번 포트를 연결시키도록 하여 컨테이너 생성 및 실행
```

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/b116258b-8007-4ed1-b829-13e202c058cf">

- Azure Context 만들기

<br>

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/cbb7f09b-90d8-4049-a95e-a9c42f610f14">

- hummingbird를 선택하였고 "docker context ls"로 Docker 컨텍스트에 ACI 컨텍스트를 추가했음을 확인한다
- "docker context use myacicontext"로 ACI 컨텍스트로 변경, 모든 후속 Docker 명령은 이 컨텍스트에서 실행된다   
    cf) "docker context use default"로 원래 상태로 돌아갈 수 있다

<br>

<img width="600" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/ecdb1c46-0c01-4bfa-bc30-cfeccb9a2fc2">

- 생성된 chomradb라는 이름의 컨테이너 인스턴스의 IP주소와 열린 Port 번호를 조합하여 외부에서 접속이 되는 것을 확인할 수 있다
- **중요한 것은 Dockerfile에서 실행하는 명령어에서 "127.0.0.1"로 host를 잡으면 로컬만 허용하고 외부 접속을 닫아서 연결되지 않는다**
- **따라서 반드시 Dockerfile에서 실행하는 명령어 부분의 host는 "0.0.0.0"으로 설정해야 한다**

<br>

# GPU 리소스를 사용하는 컨테이너 인스턴스 배포

<img width="1102" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/ba217e36-861a-49d0-a14d-e8251cd0a72e">

- GPU 리소스를 사용하기 위해서는 맨 하단에 '크기'를 수정해야 한다
- 이 경우, 모든 지역에서 GPU 리소스를 지원하지 않는다. 따라서 지원하는 지역으로 변경해줄 필요가 있다(여기서는 EastUS)   
    cf) "미국 동부, 서유럽, 미국 서부2" 이 대표적으로 GPU 리소스를 허용하는 지역이다 
- 또한 '네트워킹'에서는 포트를 8000(FastAPI의 default)로 열어주어야 한다


<br>

# Github branch 이용

<img width="800" src="https://github.com/namkidong98/flask/assets/113520117/958da870-1996-4690-8254-ffb0e23c98a1">

```
git pull      # git에서 달라진 부분을 우선 가져오기
# 코드 달라진 부분들 수정

git branch    # 현재 branch명 확인
git status    # 달라진 파일 확인
git add .     # 달라진 파일 모두 add
git commit -m "commit comment"    # commit
git push origin (branch name)     # 해당 branch에 push
```

<br>

# DockeHub에 Image 업로드

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/558f76eb-b0a2-4e6e-a1b2-9ad6efc8c4cd">

```
# Dockerfile 작성된 상태
# Docker Desktop이 열려 있는 상태
docker build --no-cache -t hummingbird_server .
```

- Docker Desktop(Local)에 "docker build"로 이미지 빌드하기

<br>

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/62357d4f-57ca-4bad-9ebc-0b456297314d">

```
docker login     # DockerHub에 접속

# General
docker tag local-image:tagname new-repo:tagname
docker push new-repo:tagname

# Example
docker tag hummingbird_server kidong98/hummingbird_server
docker push kidong98/hummingbird_server
```

- Docker Desktop에 있는 Local image에 tag를 설정하고 DockerHub에 push하기

<br>

<img width="800" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/c753af1d-638d-446d-aac5-7e58c01c29d9">

- DockerHub에 push된 상태를 확인 가능

<br>

<img width="700" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/68a72043-8dc0-40ce-a908-d78247caa577">
<img width="700" alt="image" src="https://github.com/namkidong98/flask/assets/113520117/73b8428f-3807-432b-adf8-a8fb6acebe87">

```
docker images                            # 기존의 docker 이미지들을 확인
docker pull kidong98/hummingbird_server  # DockerHub에서 Image 가져오기
docker images                            # Docker Image가 추가된 것을 확인
docker run --gpus all -p 8000:8000 --name server kidong98/hummingbird_server    # GPU를 사용하는 옵션과 포트를 열고 Container 생성
```
- DockerHub에 올린 Image를 가져와서 GPU를 사용하는 옵션으로 실행(컨테이너 생성)
