import datetime
from typing import Optional
from fastapi.params import Query
import pytz

from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId


client = MongoClient('mongodb://localhost:27017/')

db = client['lambda_ps']

users = db.users
problems = db.problems


# 경고! 보안 전혀 신경 안쓴 작품임

# 사용자 존재 여부 체크
def _check_user(username: str, nickname=None):
    res = users.find_one({'username': username})
    
    if res:
        return True
    else:
        if nickname:
            nick = users.find_one({'nickname': nickname})
            if nick:
                return True
        else:
            return False


# 사용자 생성
def create_user(username: str, password: str, nickname: str, bio: str):
    username = username.strip()

    if 'admin' in username:
        return False

    if _check_user(username, nickname):
        return False

    # 사용자 생성
    now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))
    user = {
        'username': username,
        'password': password,
        'created': now,
        'nickname': nickname,
        'bio': bio,
        'solved': [],
        'score': 0,
    }

    u_id = users.insert_one(user).inserted_id
    # ObjectId(...)
    return str(u_id)


def get_user(username: str, password=None):
    if password:
        user = users.find_one({'username': username, 'password': password})
    else:
        user = users.find_one({'username': username})

    if user:
        return {
            'username': user['username'],
            'created': user['created'],
            'nickname': user['nickname'],
            'bio': user['bio'],
            'solved': user['solved'],
            'score': user['score'],
            'num_solved': len(user['solved'])
        }
    else:
        return None


def get_rank():
    q = users.find().sort('score', -1)
    result = []
    

    for user in q:
        result.append({
            'username': user['username'],
            'nickname': user['nickname'],
            'score': user['score'],
            'num_solved': len(user['solved'])
        })

    return result


# 문제 생성
def create_problem(data: dict):
    # 실제 존재하는 유저인지 확인
    if get_user(data['author']):
        # 사용자 생성
        now = datetime.datetime.now(tz=pytz.timezone('Asia/Seoul'))
        data['created'] = now
        data['success'] = []
        p_id = problems.insert_one(data).inserted_id
        # ObjectId(...)
        return str(p_id)
        
    else:
        return False

# 문제 조회
def get_problem(id: str):
    try:
        problem = problems.find_one({'_id': ObjectId(id)})
    except InvalidId:
        return False

    if problem:
        problem['id'] = str(problem['_id'])
        problem['success_num'] = len(problem['success'])
        del problem['_id']
        return problem
    else:
        return False

# 문제 풀이자 추가
def append_successor(id: str, username: str):
    try:
        # 이미 풀려 있으면 추가 증분 없음.
        problems.find_one_and_update({'_id': ObjectId(id), 'success': {'$nin': [username]}}, {'$push': { 'success': username }})
    except InvalidId:
        pass
    return

# 계정 레벨업
def levelup_user(username: str, id: str, score: int):
    # 이미 풀려 있으면 추가 증분 없음.
    users.find_one_and_update({'username': username, 'solved': {'$nin': [id]}}, {'$push': { 'solved': id }, '$inc': { 'score': score }})
    return

# 문제 목록
def list_problems():
    q = problems.find().sort('created', -1)

    result = []
    
    for problem in q:
        result.append({
            'id': str(problem['_id']),
            'title': problem['title'],
            'author': problem['author'],
            'created': problem['created'],
            'testcases': problem['testcases'],
            'description': problem['description'],
            'success_num': len(problem['success'])
        })

    return result
    


if __name__ == '__main__':
    # 테스트
    print(_check_user('senpai'))
    print(_check_user('donotexist'))

    # print(create_user('kouhai', 'powersex', '히히힛', 'ㅁㄴㅇㄹㄴㅁㅇㄹ'))
    print(get_user('kouhai'))

    # print(create_user('elon', 'powersex', '머스크캣걸', '고양이를 만듭니다.'))
    print(get_user('elon'))

    # print(create_user('test', 'powersex', '히히힛', 'ㅁㄴㅇㄹㄴㅁㅇㄹ'))    # 안되야 정상
    print(get_user('test'))

    # print(create_user('furry', 'powersex', '오서준', '퍼리를 봅니다.'))
    print(get_user('furry'))

    print(get_rank())