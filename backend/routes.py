import json
from backend import application
from flask import request, render_template, redirect, url_for, jsonify, session
from backend.views import get_geo_value ,create_comment ,print_geo_value, get_api_total, add_member, validate_member, validate_ID, validate_PW, account_Check, create_api_data, update_api_data
from firebase_admin import db
from datetime import datetime
import math

@application.route('/', methods=['GET'])
def index():
    return render_template('home.html')
    # if 'nickname' in session:
    #     return session['nickname']
    # else:
    #     return render_template('home.html')

@application.route('/get-sesstion', methods=['GET'])
def get_sesstion():
    id = session['id']
    if(id):
        return id
    else:
        return None

@application.route('/around', methods=['POST'])
def around():
    address = request.form['address']
    
    if address:
        # 기존 세션 주소와 비교
        if 'address' in session and session['address'] == address:
            # 주소가 이미 세션에 저장된 주소와 동일한 경우
            top = session['top']
        else:
            # 주소가 새로운 경우
            top = print_geo_value(address)
            # 세션에 주소와 결과 저장
            session['address'] = address
            session['top'] = top
    else:
        return redirect('/')
    
    return render_template('around.html', item=top)
    # address = request.form['address']
    # if address:
    #     top = print_geo_value(address)
    #     return render_template('around.html', item=top)
    # else:
    #     return redirect('/')
    #return print_geo_value()

@application.route('/detail', methods=['GET'])
def detail():
    name = request.args.get('name')
    # lat = request.args.get('lat')
    # lng = request.args.get('lng')

    processed_name = str(name).replace('/', '_').replace('(', '_').replace(')', '_').replace('.', '_').replace('$', '_').replace('#', '_').replace('[', '_').replace(']', '_')
    # name = str(name).replace('/', '_').replace('(', '_').replace(')', '_').replace('.', '_').replace('$', '_').replace('#', '_').replace('[', '_').replace(']', '_')
    print(processed_name)
    ref = db.reference('piece')
    # piece = ref.order_by_child('year').equal_to(str(processed_name)).get()
    piece = ref.order_by_child('year')
    result = []
    snapshot = piece.get()
    for key, value in snapshot.items():
        if key == processed_name:
            address = value['address']
            geo_value = get_geo_value(str(address))
            if geo_value:
                value['lat'] = geo_value['lat']
                value['lng'] = geo_value['lng']
            else:
                value['lat'] = str(None)
                value['lng'] = str(None)
            result.append(value)

    comment_list = []
    ref2 = db.reference('comment')
    comments = ref2.order_by_child('time').get()
    if comments is not None:
        for comment_key, comment_value in comments.items():
            if comment_value['piece'] == name:
                time_string = comment_value['time']
                time_obj = datetime.fromisoformat(time_string)
                formatted_time = time_obj.strftime('%Y년 %m월 %d일 %H시 %M분')
                comment_value['formatted_time'] = formatted_time
                comment_list.append(comment_value)
    
    keys = ref2.order_by_key().get()
    if keys is not None:
        total = len(keys)
    else:
        total = 0

    return render_template('detail.html', piece=result, comment=comment_list, total=total)

@application.route('/comment', methods=['POST'])
def comment():
    name = request.form['name']
    comment_content = request.form['comment_content']
    person = request.form['person']

    create_comment(name, comment_content, person)

    return redirect(url_for('detail', name=name))

@application.route('/delete-comment', methods=['POST'])
def delete_comment():
    data = json.loads(request.data)  # 요청의 JSON 데이터를 파싱합니다.
    person = data.get('person')  # person 값을 가져옵니다.
    time = data.get('time')  # time 값을 가져옵니다.
    piece = data.get('piece')  # piece 값을 가져옵니다.

    ref = db.reference('comment')
    comment = ref.get()

    comment_key = None

    for key, value in comment.items():
        if value['time'] == time and value['person'] == person and value['piece'] == piece:
            comment_key = key

    print(comment_key, person, time, piece)

    if(comment_key):
        ref.child(comment_key).delete()    

    return redirect(url_for('detail', name=piece))


@application.route('/quiz', methods=['GET'])
def quiz():
    date = datetime.today().strftime("%Y%m%d%H%M%S")
    question = [["인어공주 동상", "여행자들", "내가 죽기 전에", "프란츠 카프카의 머리", "러버덕"],
                ["숟가락 다리와 체리", "시리아 이민자의 아들", "7000그루의 떡갈나무", "클라우드 게이트", "양자 클라우드"],
                ["모국이 부른다", "풍선과 소녀", "무제", "기울어진 호", "북쪽의 천사"],
                ["칼레의 시민", "키스", "다윗", "크리스탈 퀼트", "월가 황소상"],
                ["원반 던지는 사람", "사모트라케의 니케", "호박", "마망", "산타로사"]]
    images = [url_for('static', filename='img/question/러버덕.jpeg'),
              url_for('static', filename='img/question/7000나무.jpg'),
              url_for('static', filename='img/question/북쪽의천사.png'),
              url_for('static', filename='img/question/크리스탈.jpg'),
              url_for('static', filename='img/question/호박.jpg')]
    
    return render_template('quiz.html', question=question, date=date, images=images)

@application.route('/quizresult', methods=['GET'])
def quizresult():
    correct_count = 0

    omr = request.args.get('omr')  # URL의 'omr' 파라미터 값 가져오기

    if not omr:
        return "퀴즈 응답이 없습니다."

    omr = str(omr).split(",")  # ','로 구분된 문자열을 리스트로 변환

    answer = ["러버덕", "7000그루의 떡갈나무", "북쪽의 천사", "크리스탈 퀼트", "호박"]
    length = len(answer)

    if len(omr) != length:
        # 선택지 개수와 정답 개수가 일치하지 않는 경우에 대한 예외 처리
        return "퀴즈 응답이 올바르지 않습니다."

    for i in range(length):
        if omr[i] == answer[i]:
            correct_count += 20

    ref = db.reference('piece')
    keys = ref.order_by_key().get()
    total = len(keys)
    
    return render_template('quizresult.html', score=correct_count, total=total)


    #if request.method == 'GET':
    #    score = request.args.get('score', default=0, type=int)
    #    return render_template('quizresult.html', score=score)
    #elif request.method == 'POST':
    #    correct_count = 0
    #    data = request.get_json()
    #    omr = data['omr']
    #    
    #    answer = ["러버덕", "7000그루 나무", "북쪽의 천사", "크리스탈 퀼트", "호박"]
    #    length = len(answer)
#
    #    for a in range(length):
    #        if omr[a] == answer[a]:
    #            correct_count += 20
#
    #    # 리디렉션 여부와 점수를 포함한 JSON 응답 전송
    #    if correct_count == 100:  # 예시: 점수가 100일 때 리디렉션을 지시하는 경우
    #        return jsonify({'redirect': True, 'score': correct_count})
    #    else:
    #        return jsonify({'redirect': False, 'score': correct_count})

@application.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'GET':
        ref = db.reference('member')
        if 'id' in session:
            # 세션에 id가 있는 경우 처리할 내용
            id = session['id']
            member = ref.order_by_child('id').equal_to(id).get().values()
            print(member)
            return render_template('setting.html', user=member)
        else:
            # 세션에 id가 없는 경우 처리할 내용
            return redirect('login')
    if request.method == 'POST':
        id = request.form['id']
        email = request.form['email']
        nickname = request.form['nickname']
        ref = db.reference('member')

        # member 레퍼런스에서 특정 id의 정보를 가져옵니다.
        user = ref.order_by_child('id').equal_to(id).get()
        for key in user.keys():
            user_key = key
            break

        # 특정 id의 'nickname'과 'email'을 변경합니다.
        ref.child(user_key).update({
                'nickname': str(nickname),
            'email': str(email)
        })
        session['nickname'] = str(nickname)
        return redirect('/')

@application.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()
    id = data.get('id')

    ref = db.reference('member')
    user = ref.order_by_child('id').equal_to(id).get()
    for key in user.keys():
        user_key = key
        break

    ref.child(user_key).delete()    

    session.pop('nickname', None)
    session.pop('id', None)

    return jsonify(success=True)

@application.route('/list', methods=['GET', 'POST'])
def list():
    if request.method == 'GET' or request.method == 'POST':
        page = request.args.get('page')
        firstpage = False

        if page is None:
            page = 1
            firstpage = True
        else:
            page = int(page)
 
        page = int(page)

        search = request.args.get('searchquery') 
        if search is None:
            search = None

        total = int(get_api_total(search))
        x = 0
        start = 0
        end = 0

        if firstpage is True:
            if(page < 1):
                page = 1
            elif(page>total):
                page = total

            x = (page//10) # 10 // 10 = 1

            if(page%10==0):
                start = ((x-1)*10)+1
                end = ((x)*10)+1
            else:
                start = (x*10)+1
                end = ((x+1)*10)+1

            if(end > total):
                end = total+1

            return redirect(url_for('list', page=1, searchquery=search))
        elif page > total:
            if(page < 1):
                page = 1
            elif(page>total):
                page = total

            x = (page//10) # 10 // 10 = 1

            if(page%10==0):
                start = ((x-1)*10)+1
                end = ((x)*10)+1
            else:
                start = (x*10)+1
                end = ((x+1)*10)+1

            if(end > total):
                end = total+1

            return redirect(url_for('list', page=total, searchquery=search))
        elif page < 1:
            if(page < 1):
                page = 1
            elif(page>total):
                page = total

            x = (page//10) # 10 // 10 = 1

            if(page%10==0):
                start = ((x-1)*10)+1
                end = ((x)*10)+1
            else:
                start = (x*10)+1
                end = ((x+1)*10)+1

            if(end > total):
                end = total+1

            return redirect(url_for('list', page=1, searchquery=search))

        if(page < 1):
            page = 1
        elif(page>total):
            page = total
        x = (page//10) # 10 // 10 = 1
        if(page%10==0):
            start = ((x-1)*10)+1
            end = ((x)*10)+1
        else:
            start = (x*10)+1
            end = ((x+1)*10)+1
        if(end > total):
            end = total+1

        ref = db.reference('piece')
        query = ref.order_by_child('year')

        if search:
            matching_pieces = []
            for item in query.get().values():
                if search in item['name']:
                    matching_pieces.append(item)
            matching_pieces.reverse()
            start2 = (page-1)*10
            end2 = page*10
            sliced_data = matching_pieces[start2:end2]
        else:
            data = []
            for item in query.get().values():
                data.append(item)
            data.reverse() 
            # 데이터 슬라이싱
            start2 = (page-1)*10
            end2 = page*10
            sliced_data = data[start2:end2]

        return render_template('list.html', start=start, end=end, current_page=page, total=total, data=sliced_data, searchquery=search)

@application.route('/patch', methods=['GET'])
def patch():
    return render_template('patch_notes.html')

@application.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

@application.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@application.route('/logout', methods=['GET'])
def logout():
    session.pop('nickname', None)
    session.pop('id', None)
    return redirect('/')

#멤버 회원가입 조회 => 삽입
@application.route('/member', methods=['POST'])
def member():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['password']
        email = request.form['email']
        nickname = request.form['nickname']
        # 함수 리턴값으로 조건 건 다음에 리다이렉트 시키기.
        if(validate_member(id)):
            if(add_member(id, pw, email, nickname)):
                return redirect(url_for('login'))
            else:
                return redirect(url_for('signup', alertdata = True))
        else:
            return redirect(url_for('signup', alertdata = True))
    else: 
        return redirect('/')


@application.route('/checkid', methods=['POST'])
def check_id():
    if request.method == 'POST':
        data = request.get_json()
        id = data.get('id')
        return str(validate_ID(id))

@application.route('/checkpw', methods=['POST'])
def check_pw():
    if request.method == 'POST':
        data = request.get_json()
        pw = data.get('pw')
        return str(validate_PW(pw))

@application.route('/accountcheck', methods=['POST'])
def accountcheck():
    id = request.form['id']
    pw = request.form['password']
    if (account_Check(id, pw)):
        return redirect('/')
    else:
        return redirect(url_for('login', alertdata = True))

# @application.route('/getdata', methods=['GET'])
# def getdata():
#     cur_page = request.args.get('page')

#     if cur_page:
#         try:
#             cur_page = int(cur_page)
#         except ValueError:
#             cur_page = 1
#     else:
#         cur_page = 1
    
#     return get_api_piece(int(cur_page))

@application.route('/createpiece')
def createpiece():
    return create_api_data()

@application.route('/updatepiece')
def updatepiece():
    return update_api_data()

#멤버 삽입
@application.route('/fire')
def add():
    return add_member()

# @application.route('/detail')
# def index():
#     return render_template('home.html')

@application.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error=error), 404