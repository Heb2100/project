from datetime import datetime

# 현재 날짜 및 시간 가져오기
current_datetime = datetime.now()

formatted_date = current_datetime.strftime("%Y%m%d")

# 결과 출력
print("포맷팅된 날짜:", int(formatted_date) - 1)