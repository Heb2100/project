import requests, json, os
from datetime import datetime

API_KEY = "AIzaSyBqe1OKaq-bkvBhQ-s17ldtxn2OFrUSBF8"
ENGINE_ID = "361c361f92e3f45c9"
HIGH = " 상한가"
SEARCH_TYPE = "n"  # 뉴스 검색 유형
FILE_TYPE = "json"  # 결과 형식을 JSON으로 설정
LOG_PATH = "datas"

#temparary 매개변수
stocks = ['한글과컴퓨터', '파워로직스']

def main(stocks):
    print('google_search.py is running...\n', stocks)
    current_datetime = datetime.now()
    print('google_search.py is running...\n')
    today_date = current_datetime.strftime("%Y%m%d")
    print('google_search.py is running...\n')

    for stock in stocks:
        print('google_search.py stock', stock)
        url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={ENGINE_ID}&q={stock}{HIGH}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            os.makedirs(f"{LOG_PATH}/{today_date}", exist_ok=True)
            with open(f"{LOG_PATH}/{today_date}/{today_date}_news_{stock}.txt", "w", encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
        else:
            print(f"google_search.py Error status: {response.status_code}")
            print(f"google_search.py Error status: {response.text}")

if __name__ == "__main__":
    main(stocks)