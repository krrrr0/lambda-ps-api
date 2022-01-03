# 람다 동아리 온라인 저지 API 서버
## 개요
`FastAPI`와 `Mongodb`를 이용하는 람다 온라인 저지 백엔드 서버입니다. Python 3.9+ 에서 실행하세요.  
많은 보안 메커니즘들이 구현되어 있지 않아 보안에 매우 취약합니다. 주의해 주시기 바랍니다.  
  
유닉스 계열 운영체제 환경에서 실행하세요.  

## 시작하기
1. 저장소를 로컬에 클론하세요.
`git clone https://git.serve.moe/senpai/lambda-ps-api`  

2. 가상 환경을 설정하고, 의존성을 설치합니다.
`virtualenv venv`  
`source venv/bin/activate`  
`pip install -r req.txt`  
이 외에도 `Mongodb`가 필요합니다.

3. `Uvicorn` 서버를 시작합니다.
`uvicorn main:app`  
  
`localhost:8000`에 서버가 실행됩니다.  
  
Enjoy!

## 라이선스
본 코드는 [WTFPL](https://wtfpl.net/) 라이선스로 배포됩니다.  
저작자는 코드의 작동에 대한 보증을 하지 않으며, 이 소프트웨어로 인해 야기된 것에 대한 어떠한 책임도 지지 않습니다.
