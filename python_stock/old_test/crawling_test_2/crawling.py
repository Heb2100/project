import requests # requests 모듈 불러오기
from bs4 import BeautifulSoup # bs4 모듈 불러오기
import pandas as pd # pandas 모듈 불러오기
 
resp = requests.get('https://finance.naver.com/sise/sise_rise.naver') # GET 방식 크롤링
html = resp.text # HTTP Request를 보낸 URL에서 readable한 내용을 가져옴
soup = BeautifulSoup(html, 'html.parser') # HTML 코드 형태로 구분

# Find the table with the class "type_2"
table = soup.find('table', class_='type_2')
#with open("./table.txt", "w") as file:
#    file.write(str(table))
# Check if the table is found
if table:
    # Find the first row in the table (skipping the header row)
    first_row = table.find('tr', {'class': ''})

    # Check if the first row is found
    if first_row:
        # Find the second cell in the first row (which contains the stock name)
        stock_name_cell = first_row.find_all('td')[1]

        # Check if the stock name cell is found
        if stock_name_cell:
            # Extract the text content from the cell
            stock_name = stock_name_cell.text.strip()

            print("Stock Name:", stock_name)
        else:
            print("Stock name cell not found.")
    else:
        print("First row not found.")
else:
    print("Table with class 'type_2' not found.")


# news = soup.select('.tab_style_1') # 원하는 영역의 내용 가져오기
# with open("./news.txt", "w") as file:
#     file.write(str(news))
 
