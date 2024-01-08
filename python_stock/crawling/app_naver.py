from data import get_naver_news, test_KOSDQ

from datetime import datetime

# 현재 날짜 및 시간 가져오기
current_datetime = datetime.now()

formatted_date = current_datetime.strftime("%Y%m%d")

base_url = "https://news.naver.com/main/list.naver?mode=LS2D&sid2=259&sid1=101&mid=shm&date=20240108&page="
ans = []

tmp = test_KOSDQ.KOSDQ(); titles = []
print(len(tmp))
for idx, sentence in enumerate(tmp):
    if len(sentence) > idx and sentence[3] is not None and idx > 0:
        titles.append(sentence[3])
print(ans)


#for page in range(1, 28):
#    url = f"{base_url}{page}"
#    ans = get_naver_news.title_getter(url, titles, ans)
#for idx, sentences in enumerate(ans):
#    print(titles[idx])
#    for sentence in sentences:
#        print(sentence)
#    print()