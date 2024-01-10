import asyncio

from data import test_KOSDQ, test_KOSPI, google_search_result, google_search, chatgpt
from tel import tel_send_user

def parsing_data(tmp):
    l = []; tmp_send = []; stocks = []; google_reasons = []
    for i in range(10):
        try:
            tmp_row = ("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}".format(tmp[i][3], tmp[i][4], tmp[i][5], tmp[i][6], tmp[i][7], tmp[i][8], tmp[i][9], tmp[i][10], tmp[i][11]))
            tmp_send.append(tmp_row)
        except Exception as e:
            l.append('\n')
    google_search.main(stocks)
    google_reasons = google_search_result.main(stocks)
    tmp = '\n'.join(tmp_send)
    print('tmp', tmp)
    return tmp

def get_google_reason(stocks):
    google_reasons = []
    return google_reasons

def telegram_send(tmp):
    result = parsing_data(tmp)
    tel_send_user.main(result)

telegram_send(test_KOSDQ.KOSDQ())
telegram_send(test_KOSPI.KOSPI())



# module that will updated right now