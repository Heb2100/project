from openai import OpenAI
import json, os, re
from datetime import datetime


current_datetime = datetime.now()
today_date = int(current_datetime.strftime("%Y%m%d"))
stocks = ['한화투자증권', '한화투자증권우']
# stock = '한글과컴퓨터'

RESULT_DIR = f"datas/{today_date}"
GPT_CMD = """
이 주식이 오늘 상한가를 기록한 이유를 키워드 중심으로 한문장으로 요약해줄 수 있어?
"""

def main(stocks):
    print('chatgpt.py is running...\n')
    client = OpenAI(
        # key for ahope computer
        # api_key='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'
        # key for home computer
        api_key='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'
    )
    input_data = ""
    with open(f"{RESULT_DIR}/{today_date}_gpt_input.txt", "r", encoding="utf-8") as file:
        input_data = file.read()

    return_data = []
    with open(f"{RESULT_DIR}/{today_date}_gpt_output.txt", "w", encoding="utf-8") as output_file:
        for stock_idx, stock in enumerate(stocks):
            # input data slicing
            start_pattern = "<<"; end_pattern = "<<"; start_index = 0; input_sliced_datas = []
            while start_index != -1:
                start_index = input_data.find(start_pattern, start_index)
                if start_index != -1:
                    end_index = input_data.find(end_pattern, start_index + 1) - 3
                    if end_index != -1:
                        sliced_text = input_data[start_index:end_index + len(end_pattern)]
                        input_sliced_datas.append(sliced_text)
                        start_index = end_index + len(end_pattern)
                    else:
                        sliced_text = input_data[start_index:]
                        input_sliced_datas.append(sliced_text)
                        break
                else:
                    print("시작 패턴이 발견되지 않았습니다.")
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": f"{input_sliced_datas[stock_idx]}\n\n{GPT_CMD}",
                    }
                ],
                model="gpt-3.5-turbo",
                stream=True,
            )
            gpt_ans = ""
            for chunk in chat_completion:
                gpt_ans += chunk.choices[0].delta.content or ""

            output_file.write(stock + '\n')
            output_file.write(gpt_ans + '\n')
            return_data.append(gpt_ans)
    return return_data




if __name__ == "__main__":
    main(stocks)