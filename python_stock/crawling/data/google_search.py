import requests, json, os
from datetime import datetime

API_KEY = "AIzaSyBqe1OKaq-bkvBhQ-s17ldtxn2OFrUSBF8"
ENGINE_ID = "361c361f92e3f45c9"
HIGH = " 상한가"
SEARCH_TYPE = "n"  # 뉴스 검색 유형
FILE_TYPE = "json"  # 결과 형식을 JSON으로 설정
LOG_PATH = "datas"

#temparary 매개변수
titles = ['파워로직스', '이스트소프트', '한빛레이저', '바이브컴퍼니', '유니트론텍', '아이원', '제넨바이오', '티와이홀딩스']

def main(titles):
    current_datetime = datetime.now()
    today_date = current_datetime.strftime("%Y%m%d")

    for title in titles:
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={ENGINE_ID}&q={title}{HIGH}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            print(data)
            os.makedirs(f"{LOG_PATH}/{today_date}", exist_ok=True)
            with open(f"{LOG_PATH}/{today_date}/news_{today_date}_{title}.txt", "w", encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        else:
            print(f"google_search.py Error status: {response.status_code}")
            print(f"google_search.py Error status: {response.text}")

if __name__ == "__main__":
    main(titles)