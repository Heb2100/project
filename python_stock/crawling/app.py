import asyncio, os

from data import upper_limit, google_search_result, google_search, chatgpt
from tel import tel_send_user
from datetime import datetime


current_datetime = datetime.now()
today_date = current_datetime.strftime("%Y%m%d")
def parsing_data(tmp):
    l = []; stock_datas = []; stocks = []; parsed_data = []; gpt_datas = []
    for i in range(10):
        try:
            tmp_row = ("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(tmp[i][3], tmp[i][4], tmp[i][5], tmp[i][6], tmp[i][7], tmp[i][8], tmp[i][9], tmp[i][10], tmp[i][11]))
            stock_datas.append(tmp_row)
            if i != 0 and tmp[i][3]: stocks.append(tmp[i][3])
        except Exception as e:
            l.append('\n')
    if not os.path.exists(f"datas/{today_date}/{today_date}_news_{stocks[0]}.txt"):
        google_search.main(stocks)
    if not os.path.exists(f"datas/{today_date}/{today_date}_gpt_input.txt"):
        google_search_result.main(stocks)
    if not os.path.exists(f"datas/{today_date}/{today_date}_gpt_output.txt"):
        gpt_datas = chatgpt.main(stocks)
    else:
        with open(f"datas/{today_date}/{today_date}_gpt_output.txt", 'r') as file:
            for line_number, line in enumerate(file, 1):
                if line_number % 2 == 0:
                    gpt_datas.append(line.strip())
    print('gpt_datas', gpt_datas, '\n stock_datas', stock_datas)
    parsed_data.append(stock_datas[0])
    for i in range(len(stocks)):
        parsed_data.append(stock_datas[i+1])
        parsed_data.append(gpt_datas[i])
    parsed_data = '\n'.join(parsed_data)
    print('parsed_data', parsed_data)
    return parsed_data

def telegram_send(tmp):
    result = parsing_data(tmp)
    tel_send_user.main(result)

# telegram_send(test_KOSDQ.KOSDQ())
telegram_send(upper_limit.main())



# module that will updated right now