from openai import OpenAI
import json, os, re
from datetime import datetime


current_datetime = datetime.now()
today_date = current_datetime.strftime("%Y%m%d")
stocks = ['한글과컴퓨터', '파워로직스', '이스트소프트', '한빛레이저', '바이브컴퍼니', '유니트론텍', '아이원', '제넨바이오', '티와이홀딩스']
stock = '한글과컴퓨터'

RESULT_DIR = f"./data/{today_date}"
GPT_CMD = """
이 주식이 오늘 상한가를 기록한 이유를 한문장으로 요약해줄 수 있어?
"""

client = OpenAI(
    # This is the default and can be omitted
    api_key='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'
)
# input_data = ""
# with open(f"{RESULT_DIR}/{today_date}_gpt_input.txt", "r") as file:
#     input_data = file.read()


# # input data slicing
# start_pattern = "<<"; end_pattern = "<<"; start_index = 0; input_sliced_datas = []
# while start_index != -1:
#     start_index = input_data.find(start_pattern, start_index)
#     if start_index != -1:
#         end_index = input_data.find(end_pattern, start_index + 1) - 3
#         if end_index != -1:
#             sliced_text = input_data[start_index:end_index + len(end_pattern)]
#             print(sliced_text)
#             input_sliced_datas.append(sliced_text)
#             start_index = end_index + len(end_pattern)
#         else:
#             print("끝 패턴이 발견되지 않았습니다.")
#             break
#     else:
#         print("시작 패턴이 발견되지 않았습니다.")

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            # "content": f"{input_sliced_datas[0]}\n\n{GPT_CMD}",
            "content": "자기소개 해줘",
        }
    ],
    model="gpt-3.5-turbo",
    stream=True,
)
tmp = ""
for chunk in chat_completion:
    tmp += chunk.choices[0].delta.content or ""

# 나중에 tmp를 필요한 곳에서 사용
print(tmp)