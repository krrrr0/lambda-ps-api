from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware


from connect import mongodb
from tools import jwttools
from tools import sandbox

app = FastAPI()

# TODO
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "YOUR_URL_HERE"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    username: str
    password: str
    nickname: Optional[str]
    bio: Optional[str]


class _TestCase(BaseModel):
    in_: str
    out: str
    description: str

    class Config:
        fields = {
            'in_': 'in'
        }


class Problem(BaseModel):
    testcases: list[_TestCase]
    description: str
    title: str


class SolveProblem(BaseModel):
    id: str
    code: str
    lang: str



@app.get("/")
def read_root():
    return {"여러분!": "블루아카는 갓겜입니다!"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.post("/user", status_code=201)
def create_user(user: User):
    if len(user.password) < 6:
        return {
            'result': 'error',
            'message': '비밀번호는 6자 이상으로!'
        }

    username = user.username.lower()

    result = mongodb.create_user(username, user.password, user.nickname, user.bio)

    if result:
        # Issue JWT
        jwt = jwttools.issue_jwt(username, user.nickname)

        return {
            'result': 'success',
            'data': {
                'token': jwt
            }
        }
    
    else:
        return {
            'result': 'error',
            'message': '이미 사용 중인 사용자 이름/닉네임입니다. 다른 이름으로 시도해 주세요.'
        }


# 사용자 조회
@app.get('/info')
def get_info(jwt: Optional[str] = Cookie(None)):
    if jwt:
        decoded = jwttools.validate_jwt(jwt)

        if not decoded:
            return {
                'result': 'error',
                'message': '토큰 오류'
            }
        else:
            return {
                'result': 'success',
                'data':{
                    'username': decoded['username'],
                    'nickname': decoded['nickname']
                }
            }
    else:
        return {
            'result': 'error',
            'message': '토큰 오류'
        }


# 사용자 조회
@app.get('/user')
def get_user(username: str, token: Optional[str] = None):
    result = mongodb.get_user(username)

    if result:
        if token:
            # JWT 확인
            decoded = jwttools.validate_jwt(token)

            if not decoded:
                return {
                    'result': 'error',
                    'message': '토큰 오류'
                }

            # 자기꺼 조회시에는
            if username == decoded['username']:
                # 나중에 필요시 구현
                print('디버그: 동일인물')
                return {
                    'result': 'success',
                    'data': result
                }

        return {
            'result': 'success',
            'data': result
        }
    
    else:
        return {
            'result': 'error',
            'message': '그런 사람은 읎어요'
        }

@app.post("/logout")
def logout(response: Response):

    response.set_cookie(key="jwt", value='', samesite="none", httponly=True)

    return {
        'result': 'success'
    }


@app.post("/login")
def login(user: User, response: Response):
    username = user.username.lower()
    result = mongodb.get_user(username, user.password)

    if result:
        # Issue JWT
        jwt = jwttools.issue_jwt(username, result['nickname'])

        response.set_cookie(key="jwt", value=jwt, samesite="none", httponly=True)

        return {
            'result': 'success',
            'data': {
                'token': jwt
            }
        }
    
    else:
        return {
            'result': 'error',
            'message': '로그인 실패! ㅋㅋㅋ'
        }


@app.get('/rank')
def get_rank():
    """
    {'username': 'elon', 'nickname': '머스크캣걸', 'score': 3453535, 'num_solved': 0}
    """
    return {
        'result': 'success',
        'data': mongodb.get_rank()
    }

# 문제 등록
@app.post('/p')
def create_problem(params: Problem, jwt: Optional[str] = Cookie(None)):
    """
    DB 구조:
    {
        _id: ...
        author: str
        testcases: [
            {
                in
                out
                description
            }
        ]
        description: str (마크다운)
        success: [  # 사용자 이름
            str
            str
            ...
        ]
    }
    """

    if not jwt:
        return {
            'result': 'error',
            'message': '토큰 오류'
        }

    # JWT Auth
    decoded = jwttools.validate_jwt(jwt)

    if not decoded:
        return {
            'result': 'error',
            'message': '토큰 오류'
        }

    tc = []
    for i in params.testcases:
        a = i.dict()
        a['in'] = a.pop('in_')
        tc.append(a)

    req = {
        'testcases': tc,
        'description': params.description,
        'author': decoded['username'],
        'title': params.title.strip()
    }

    result = mongodb.create_problem(req)
    
    if result:
        return {
            'result': 'success',
            'data': {
                'id': result
            }
        }

    else:
        return {
            'result': 'error',
            'message': '문제 생성 실패'
        }
    # 문제 고유 id 나 이런걸 돌려줘야겠지?


@app.get('/p')
def get_problems(id: Optional[str] = None):
    # 이미 풀이한 문제는 클라에서 따로 user get 요청 때려서 처리.
    # id가 주어질 경우에는 주어진 문제꺼를 가져오고, 아니면 전부다(리스트를) 가져온다.
    if id:
        result = mongodb.get_problem(id)

        if result:
            return {
                'result': 'success',
                'data': result
            }
        else:
            return {
                'result': 'error',
                'message': 'Not Found'
            }
    else:
        result = mongodb.list_problems()

        return {
            'result': 'success',
            'data': result
        }


# 문제 풀이 시도
@app.post('/solve')
def solve(params: SolveProblem, jwt: Optional[str] = Cookie(None)):
    # params.id
    # params.lang
    # params.code

    if not jwt:
        return {
            'result': 'error',
            'message': '토큰 오류'
        }


    # JWT Auth
    decoded = jwttools.validate_jwt(jwt)

    if not decoded:
        return {
            'result': 'error',
            'message': '토큰 오류'
        }
    
    problem = mongodb.get_problem(params.id)

    if problem:
        for testcase in problem['testcases']:
            out, err, timeout = sandbox.execute_in_sandbox(params.code, params.lang, testcase['in'].strip() + '\n')
            if timeout:
                return {
                    'result': 'fail',
                    'data': {
                        'message': '타임아웃: 제한 시간 5초를 초과했습니다.',
                        'out': out.strip(),
                        'err': err.strip(),
                        'expected': testcase['out'].strip()
                    }
                }
            elif err:
                return {
                    'result': 'fail',
                    'data': {
                        'message': '오류가 발생했습니다:',
                        'out': out.strip(),
                        'err': err.strip(),
                        'expected': testcase['out'].strip()
                    }
                }
            else:
                if out.strip() == testcase['out'].strip():
                    continue
                else:
                    return {
                        'result': 'fail',
                        'data': {
                            'message': '틀렸습니다: 테스트케이스 검증 실패!',
                            'out': out.strip(),
                            'err': '',
                            'expected': testcase['out'].strip()
                        }
                    }
        # 성공했을 경우
        mongodb.append_successor(params.id, decoded['username'])
        mongodb.levelup_user(decoded['username'], params.id, 100)
        return {
            'result': 'success',
            'data': {
                'message': '정답!',
                'out': out.strip(),
                'err': '',
                'expected': testcase['out'].strip()
            }
        }

    else:
        return {
            'result': 'error',
            'message': '그런 문제는 읎어요'
        }

    

    # 지정된 언어 샌드박스 실행후 결과 비교

    # 풀었으면 유저 (score, solved: id), 문제(success append) 수정한후 success 리턴

    pass


# 필요한 기능
# 1. 회원가입 v / 로그인 v / 유저 푼문제 v , 랭킹 v , etc.
# 2. 문제 등록 (stdin/stdout) / 솔빙처리, 기록 / 문제 목록
# 3. 문제 solve
