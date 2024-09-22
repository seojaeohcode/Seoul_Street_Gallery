from flask import Flask, request, jsonify, session
from geopy.geocoders import Nominatim
import requests
import json
from config import firebase_admin
from firebase_admin import db
import random
import xmltodict
import math
import datetime
import pytz


def add_member(id, pw, email, nickname):
    a = ["성실한", "진지한"]
    b = ["피카소", "살바도르 달리"]

    trim_nickname = str(nickname).replace(" ", "")
    trim_email = str(email).replace(" ", "")

    if trim_nickname == "" or trim_nickname == None or len(trim_nickname) < 2:
        nickname = str(random.choice(a) + " " + random.choice(b))

    if trim_email == None or trim_email == "":
        email = "none@gmail.com"

    ref = db.reference("member")  # 기본 가장 상단을 가르킴
    # user_ref = ref.push()
    # user_ref.set({
    #    'id' : str(id),
    #    'password' : str(pw),
    #    'nickname' : str(nickname),
    #    'email' : str(email)
    #    })
    ref.child(str(id)).set(
        {
            "id": str(id),
            "password": str(pw),
            "nickname": str(nickname),
            "email": str(email),
            "admin": False,
        }
    )
    # ref.update({'id' : 'development'}) # 해당 변수가 없으면 생성한다.
    return True


def validate_member(id):
    ref = db.reference("member")
    IDExist = ref.order_by_child("id").equal_to(id).get()
    # PWExist = ref.order_by_child('password').equal_to(pw).get()
    # NicknameExist = ref.order_by_child('id').equal_to(id).get()
    # EmailExist = ref.order_by_child('email').equal_to(id).get()

    if IDExist:
        # return jsonify({'message': 'Exist ' + result}), 200
        return False
    else:
        return True
        # return jsonify({'message': 'NoExist'}), 200
        # if PWExist:
        #     return False
        # else:
        #     return True

    # member에서 id가 id인 값을 조회
    # docs = db.collection(u'member')

    # for doc in docs:
    #    print(u'{} => {}'.format(doc.id, doc.to_dict()))


def validate_ID(id):
    ref = db.reference("member")
    IDExist = ref.order_by_child("id").equal_to(id).get()

    if IDExist:
        return "True"
    else:
        return "False"


def validate_PW(pw):
    ref = db.reference("member")
    PWExist = ref.order_by_child("password").equal_to(pw).get()

    if PWExist:
        print(True)
        return "True"
    else:
        print(False)
        return "False"


# def validate_email(email):
#     ref = db.reference('member')

#     if(email == None):
#         email = ' '

#     EmailExist = ref.order_by_child('email').equal_to(email).get()

#     if EmailExist:
#         return 'True'
#     else:
#         return 'False'


def account_Check(id, pw):
    ref = db.reference("member")
    AccountExist = ref.order_by_child("id").equal_to(id).get()

    if AccountExist:
        for key, value in AccountExist.items():
            if value.get("password") == pw:
                session["nickname"] = value.get("nickname")
                session["id"] = value.get("id")
                return True
    else:
        return False


def get_api_total(search):
    # 이전 쿼리에서 가져온 데이터 중에서 6번째 데이터의 'year' 값을 가져옴
    # ref = db.reference('piece').order_by_child('year').limit_to_first(5).get()
    # last_year = list(ref.values())[-1]['year']

    # 'year' 필드가 'last_year' 이상인 데이터 중에서 다섯 번째까지의 데이터를 가져옴
    # ref = db.reference('works').order_by_child('year').start_at(last_year).limit_to_first(5).get()
    # ref = db.reference('piece').order_by_child('year').limit_to_first(5).get()
    # 가져온 데이터를 출력함
    print(search)
    if search == None:
        ref = db.reference("piece")
        keys = ref.order_by_key().get()
        total = math.ceil(len(keys) / 10)
    else:
        ref = db.reference("piece")
        data = ref.order_by_child("year")
        matching_pieces = []
        for item in data.get().values():
            if str(search).lower() in str(item["name"]).lower():
                matching_pieces.append(item)
        total = math.ceil(len(matching_pieces) / 10)

    return str(total)


# def get_api_piece(cur_page, search):
#     ref = db.reference('piece')

#     # year 필드를 기준으로 내림차순으로 정렬된 데이터 가져오기
#     query = ref.order_by_child('year')

#     data = []
#     for item in query.get().values():
#         data.append(item)

#     data.reverse()

#     # 데이터 슬라이싱
#     start = (cur_page-1)*10
#     end = cur_page*10
#     sliced_data = data[start:end]

#     # 결과 출력
#     for item in sliced_data:
#         print(item)

#     return "ok"


def update_api_data():
    return "json?"


def create_api_data():
    ref = db.reference("")
    # piece_ref = ref.update(data_list)
    # user_ref.set()
    # user_ref = ref.push()
    # user_ref.set({
    #    'id' : str(id),
    #    'password' : str(pw),
    #    'nickname' : str(nickname),
    #    'email' : str(email)
    #    })

    url1 = "http://openapi.seoul.go.kr:8088//xml/tvGonggongArt/1/1000/"
    url2 = "http://openapi.seoul.go.kr:8088//xml/tvGonggongAllArt/1/1000/"
    url3 = "http://openapi.seoul.go.kr:8088//xml/gongGongArtEtc/1/1000/"

    response1 = requests.get(url1)
    response2 = requests.get(url2)
    response3 = requests.get(url3)

    xml_data1 = xmltodict.parse(response1.text)
    xml_data2 = xmltodict.parse(response2.text)
    xml_data3 = xmltodict.parse(response3.text)

    # data_list = []
    # data =
    # data_list.append({item['GA_KNAME']: data})

    for item in xml_data2["tvGonggongAllArt"]["row"]:
        name = str(item["GA_KNAME"])
        name = (
            name.replace("/", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace(".", "_")
            .replace("$", "_")
            .replace("#", "_")
            .replace("[", "_")
            .replace("]", "_")
        )

        ref.child("piece").child(name).set(
            {
                "name": item["GA_KNAME"],
                "year": item["GA_INS_DATE"],
                "address": item["GA_ADDR"],
                "description": "none",
            }
        )

        # data =
        # data_list.append({item['GA_KNAME']: data})
    for item in xml_data1["tvGonggongArt"]["row"]:
        name = str(item["GA_KNAME"])
        name = (
            name.replace("/", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace(".", "_")
            .replace("$", "_")
            .replace("#", "_")
            .replace("[", "_")
            .replace("]", "_")
        )

        if (
            item["GA_DETAIL"] == ""
            or item["GA_DETAIL"] == " "
            or item["GA_DETAIL"] == None
        ):
            ref.child("piece").child(name).set(
                {
                    "name": item["GA_KNAME"],
                    "year": item["GA_INS_DATE"],
                    "address": item["GA_ADDR1"],
                    "description": "none",
                }
            )
        else:
            ref.child("piece").child(name).set(
                {
                    "name": item["GA_KNAME"],
                    "year": item["GA_INS_DATE"],
                    "address": item["GA_ADDR1"],
                    "description": item["GA_DETAIL"],
                }
            )

    for item in xml_data3["gongGongArtEtc"]["row"]:
        name = str(item["GA_KNAME"])
        name = (
            name.replace("/", "_")
            .replace("(", "_")
            .replace(")", "_")
            .replace(".", "_")
            .replace("$", "_")
            .replace("#", "_")
            .replace("[", "_")
            .replace("]", "_")
        )

        if (
            item["GA_DETAIL"] == ""
            or item["GA_DETAIL"] == " "
            or item["GA_DETAIL"] == None
        ):
            ref.child("piece").child(name).set(
                {
                    "name": item["GA_KNAME"],
                    "year": item["GA_INS_DATE"],
                    "address": item["GA_ADDR1"],
                    "description": "none",
                }
            )
        else:
            ref.child("piece").child(name).set(
                {
                    "name": item["GA_KNAME"],
                    "year": item["GA_INS_DATE"],
                    "address": item["GA_ADDR1"],
                    "description": item["GA_DETAIL"],
                }
            )

        # data_list.append({item['GA_KNAME']: data})

    # 추출한 데이터를 JSON으로 변환
    # json_data = json.dumps(data_list, ensure_ascii=False)

    # soup = BeautifulSoup(response2.text, 'xml')

    # rows = soup.find_all('row')
    # data = []
    # for row in rows:
    #     item = {}
    #     item['작품명'] = row.GA_KNAME.text
    #     item['연도'] = row.GA_INS_DATE.text
    #     item['주소'] = row.GA_ADDR.text
    #     item['상세설명'] = 'none'
    #     data.append(item)

    # print(data_list)

    # json_data = json.dumps(data_list, ensure_ascii=False)

    # with open('json/artlist.json', 'w', encoding='utf-8') as f:
    #    f.write(json_data)

    return "Update"


def distance(lat1, lng1, lat2, lng2):
    # 지구의 반지름 (단위: km)
    radius = 6371

    # 각도를 라디안으로 변환
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lng1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lng2)

    # 위도와 경도의 차이 계산
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad

    # Haversine 공식 계산
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c

    return distance


def get_geo_value(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json?query=" + address
    headers = {"Authorization": ""}
    response = requests.get(url, headers=headers)
    api_json = json.loads(response.text)

    if "documents" in api_json and api_json["documents"]:
        address = api_json["documents"][0]["address"]
        crd = {"lat": str(address["y"]), "lng": str(address["x"])}
        return crd
    else:
        return None


def print_geo_value(address):
    rank = []
    top = []

    crd = get_geo_value(str(address))

    if crd is None:
        current = "Could not retrieve geolocation for the address."
    else:
        current = [crd["lat"], crd["lng"]]

    print(current)

    ref = db.reference("piece")
    data = ref.order_by_child("year")

    for item in data.get().values():
        address2 = item["address"]
        crd2 = get_geo_value(str(address2))
        if crd2:
            dis = distance(
                float(current[0]),
                float(current[1]),
                float(crd2["lat"]),
                float(crd2["lng"]),
            )
            rank.append(
                [
                    item["name"],
                    item["address"],
                    item["year"],
                    dis,
                    current[0],
                    current[1],
                ]
            )
        # else:
        # print(str(item['name']) + ': no lat&lng')

    rank.sort(key=lambda x: x[3])

    top = [rank[0], rank[1], rank[2]]

    for i in range(3):
        top[i][3] = round(top[i][3], 1)

    print(top)

    return top


def create_comment(piece, comment, person):
    ref = db.reference("comment")  # 기본 가장 상단을 가르킴
    ref2 = db.reference("member")
    mem = ref2.order_by_child("id").equal_to(person).get()
    nickname = ""
    for key, value in mem.items():
        nickname = value["nickname"]

    # 현재 시간 가져오기
    current_time = datetime.datetime.now(pytz.UTC)

    # ISO 8601 형식으로 변환
    time_string = current_time.isoformat()

    comment_ref = ref.push()
    comment_ref.set(
        {
            "piece": str(piece),  # 어느 작품
            "content": str(comment),  # 무슨 내용
            "person": str(person),  # 누가
            "nickname": str(nickname),
            "time": str(time_string),  # 언제 달렸는지
        }
    )
    return True


# def get_geo_value(address):
#    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + address
#    headers = {"Authorization": ""}
#    api_json = json.loads(str(requests.get(url,headers=headers).text))
#    address = api_json['documents'][0]['address']
#    crd = {"lat": str(address['y']), "lng": str(address['x'])}
#    #address_name = address['address_name']
#
#    return crd
#
#    #geolocoder = Nominatim(user_agent = 'South Korea', timeout=None)
#    #geo = geolocoder.geocode(address)
#    #crd = {"lat": str(geo.latitude), "lng": str(geo.longitude)}
##
#    #return crd
#
# def print_geo_value(address):
#    rank = []
#    top = []
#
#    crd = get_geo_value(str(address))
#
#    if crd is None:
#        current = "Could not retrieve geolocation for the address."
#    else:
#        current = [crd['lat'], crd['lng']]
#
#    print(current)
#
#    ref = db.reference('piece')
#    data = ref.order_by_child('year')
#
#    for item in data.get().values():
#        address2 = item['address']
#        crd2 = get_geo_value(str(address2))
#        if crd2:
#            rank.append([item['name'], item['address'], item['year'], crd2['lat'], crd['lng']])
#        else:
#            print('no lat&lng')
#
#    return "hello"
