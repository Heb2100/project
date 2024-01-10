import json, os
from datetime import datetime
from google_search


current_datetime = datetime.now()
today_date = current_datetime.strftime("%Y%m%d")
stocks = ['한글과컴퓨터', '파워로직스', '이스트소프트', '한빛레이저', '바이브컴퍼니', '유니트론텍', '아이원', '제넨바이오', '티와이홀딩스']
RESULT_DIR = f"./data/{today_date}"
OUTPUT_FILE = f"{LOG_PATH}/{today_date}/news_{today_date}_{title}.txt"


def main(stocks):
    with open(OUTPUT_FILE, "w") as output_file:
        for stock in stocks:

            stored_data = ""
            with open(f"{RESULT_DIR}/news_{today_date}_{stock}.txt", "r") as file:
                stored_data = file.read()
            data = json.loads(stored_data)
            titles = [item.get('title', '') for item in data.get('items', [])]
            snippets = [item.get('snippet', '') for item in data.get('items', [])]

            
            # Print titles
            print(f'<<{stock}>>')
            output_file.write(str(f'<<{stock}>>\n'))
            for i in range(len(titles)):
                print(titles[i])
                output_file.write(str(titles[i]) + "\n")
                print()
                print(snippets[i])
                output_file.write(str(snippets[i]) + "\n")
                print()
            print("\n")
            output_file.write("\n")
if __name__ == "__main__":
    main(titles)