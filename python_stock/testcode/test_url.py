from datetime import datetime

# 현재 날짜 및 시간 가져오기
current_datetime = datetime.now()

formatted_date = current_datetime.strftime("%Y%m%d")
base_url = "https://news.naver.com/main/list.naver?mode=LS2D&sid2=259&sid1=101&mid=shm&date=20240108&page="
date = str(int(formatted_date) - 1)
modified_url = base_url[:80] + date + base_url[88:]
print(modified_url)

#def base_url_generator(base_url, date):
    