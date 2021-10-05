from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb://3.34.252.62', 27017, username="test", password="test")
db = client.music_list


# 회원가입
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": "",  # 프로필 한 마디
        "pickedList": [""]
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})

# 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 로그인
@app.route('/sign_in', methods=['POST'])
def sign_in():

    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


## 로그인페이지이동
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)



## index
@app.route('/')  # 메인페이지로 이동
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = (payload["id"])

        music_list = list(db.music_list.find({}, {'_id': False}))
        return render_template("index.html", username=username, list=music_list)

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 상세페이지
@app.route('/detail/<title>')
def detail(title):
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = (payload["id"])

        pickedList = db.users.find_one({'username': username}, {'_id': False})['pickedList']

        music = db.music_list.find_one({'title': title}, {'_id': False})

        reviews = list(db.music_review.find({'title': title}))
        return render_template("detail.html", music=music, reviews=reviews, username=username, pickedList=pickedList)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))

    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


# 리뷰 작성
@app.route('/review', methods=['POST'])
def write_review():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = (payload["id"])
        contents_receive = request.form['contents_give']
        music_title_receive = request.form['music_title_give']

        doc = {
            'username': username,
            'contents': contents_receive,
            'title': music_title_receive
        }

        if contents_receive == '':
            return jsonify({'msg': '리뷰를 입력하세요!'})
        else:
            db.music_review.insert_one(doc)
            return jsonify({'msg': '저장 완료!'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


## 리뷰삭제
@app.route('/review/delete', methods=['POST'])
def delete_review():
    id_receive = request.form['target_id_give']
    db.music_review.delete_one({'_id': ObjectId(id_receive)})
    return jsonify({'msg': '삭제 완료!'})


## 좋아요
@app.route('/detail/likeUp', methods=['POST'])
def likeUp():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        username = (payload["id"])

        ## 좋아요증가
        title_receive = request.form['title_give']
        target = db.music_list.find_one({'title': title_receive})
        newlike = target['like'] + 1
        ##노래의 총 좋아요 수 업데이트
        db.music_list.update_one({'title': title_receive}, {'$set': {'like': newlike}})

        ## 사용자 좋아요 목록의 요소 추가
        db.users.update({'username': username}, {'$addToSet': {"pickedList": title_receive}})

        return jsonify({'msg': '좋아요를 누르셨습니다.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


## 좋아요취소
@app.route('/detail/likeDown', methods=['POST'])
def likeDown():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = (payload["id"])

        ## 좋아요감소
        title_receive = request.form['title_give']
        target = db.music_list.find_one({'title': title_receive})
        newlike = target['like'] - 1
        ## 노래의 총 좋아요 수 업데이트
        db.music_list.update_one({'title': title_receive}, {'$set': {'like': newlike}})

        ## 사용자 좋아요 목록의 요소 삭제
        db.users.update({'username': username}, {'$pull': {"pickedList": title_receive}})

        return jsonify({'msg': '좋아요를 취소하셨습니다.'})

    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
