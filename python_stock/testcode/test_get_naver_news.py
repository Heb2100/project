import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 현재 날짜 및 시간 가져오기
current_datetime = datetime.now()

formatted_date = current_datetime.strftime("%Y%m%d")

def title_getter(url, titles, ans):

    response = requests.get(url)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    # Extracting the sentences from the given HTML
    sentences = [[] for i in range(len(titles))] if len(ans) == 0 else ans

    # Find all the dt elements with class "photo"
    dt_elements = soup.find_all('dt', class_='photo')
    # Iterate through each dt element and extract the text from the associated dd element
    for dt_element in dt_elements:
        # Find the associated dd element
        dd_element = dt_element.find_next('dd')

        # Extract the text from the dt and dd elements
        a_element = dt_element.find('a', class_='nclicks(eco.2ndcont)')
        dt_text = a_element.find('img').get('alt')
        dd_text = dd_element.find('span', class_='lede').get_text(strip=True)

        # Combine the text from dt and dd elements to form a sentence
        sentence = f"{dt_text}"
        for idx, title in enumerate(titles):
            if title in sentence:
                sentences[idx].append(sentence)
    return sentences

    # Print the extracted sentences
#    for i in range(len(sentences)):
#        print(titles[i])
#        for sentence in sentences[i]:
#            print(sentence)
#        print()

base_url = "https://news.naver.com/main/list.naver?mode=LS2D&sid2=259&sid1=101&mid=shm&date=20240108&page="
ans = []
titles = ['한글과컴퓨터', '파워로직스', '이스트소프트', '한빛레이저', '바이브컴퍼니', '유니트론텍', '아이원', '제넨바이오', '티와이홀딩스']

for day in range(1):
    date = str(int(formatted_date) - day)
    modified_url = base_url[:80] + date + base_url[88:]
    for page in range(1, 28):
        url = f"{modified_url}{page}"
        ans = title_getter(url, titles, ans)
for idx, sentences in enumerate(ans):
    print(titles[idx])
    for sentence in sentences:
        print(sentence)
    print()