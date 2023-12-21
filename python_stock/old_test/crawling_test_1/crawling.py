import requests # requests 모듈 불러오기
from bs4 import BeautifulSoup # bs4 모듈 불러오기
import pandas as pd # pandas 모듈 불러오기
 
resp = requests.get('https://finance.naver.com/') # GET 방식 크롤링
html = resp.text # HTTP Request를 보낸 URL에서 readable한 내용을 가져옴
soup = BeautifulSoup(html, 'html.parser') # HTML 코드 형태로 구분
news = soup.select('.section_strategy') # 원하는 영역의 내용 가져오기
with open("./news.txt", "w") as file:
    file.write(str(news))
 
