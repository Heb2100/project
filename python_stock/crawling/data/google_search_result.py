import json, os
from datetime import datetime


current_datetime = datetime.now()
today_date = current_datetime.strftime("%Y%m%d")
# stocks = ['한글과컴퓨터', '파워로직스', '이스트소프트', '한빛레이저', '바이브컴퍼니', '유니트론텍', '아이원', '제넨바이오', '티와이홀딩스']
LOG_PATH = "datas"
IO_DIR = f"{LOG_PATH}/{today_date}/"


def main(stocks):
    print('google_search_result.py is running...\n')
    with open(f"{IO_DIR}/{today_date}_gpt_input.txt", "w") as output_file:
        for stock in stocks:

            stored_data = ""
            with open(f"{IO_DIR}/{today_date}_news_{stock}.txt", "r") as file:
                stored_data = file.read()
            data = json.loads(stored_data)
            titles = [item.get('title', '') for item in data.get('items', [])]
            snippets = [item.get('snippet', '') for item in data.get('items', [])]

            
            # Print titles
            output_file.write(str(f'<<{stock}>>\n'))
            for i in range(len(titles)):
                output_file.write(str(titles[i]) + "\n")
                output_file.write(str(snippets[i]) + "\n")
            output_file.write("\n")
if __name__ == "__main__":
    main(stocks)