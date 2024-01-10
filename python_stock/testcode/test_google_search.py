import requests, json
from datetime import datetime

# 현재 날짜 및 시간 가져오기
API_KEY = "AIzaSyBqe1OKaq-bkvBhQ-s17ldtxn2OFrUSBF8"
ENGINE_ID = "361c361f92e3f45c9"
SEARCH = "한글과컴퓨터 상한가"
HIGH = " 상한가"
# 추가된 매개변수
SEARCH_TYPE = "n"  # 뉴스 검색 유형
FILE_TYPE = "json"  # 결과 형식을 JSON으로 설정

current_datetime = datetime.now()
today_date = current_datetime.strftime("%Y%m%d")

titles = ['파워로직스', '이스트소프트', '한빛레이저', '바이브컴퍼니', '유니트론텍', '아이원', '제넨바이오', '티와이홀딩스']

for title in titles:
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={ENGINE_ID}&q={title}{HIGH}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        # 여기에서 원하는 작업을 수행하세요
        print(data)
        # with open("./news_default.txt", "w") as file:
        #     file.write(str(data))
        with open(f"./news_{today_date}_{title}.txt", "w", encoding='utf-8') as file:
            # indent 매개변수를 사용하여 들여쓰기 수준을 지정할 수 있습니다.
            json.dump(data, file, ensure_ascii=False, indent=2)
    else:
        print(f"Error status: {response.status_code}")
        print(f"Error status: {response.text}")