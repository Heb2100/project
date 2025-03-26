stocks = ['한화투자중권', '한화투자중권우']
gpt_datas = ['한화투자증권 관련 주식들이 토스와 토큰 수혜 관련 소식에 강세를 보이며 상한가를 기록했다.', '한화투자증권우가 비트코인 상승으로 인해 토큰 수혜주로 주목받아 오늘도 상한가를 기록했다.'] 
stock_datas = ['종목명\t현재가\t전일비\t등락률\t거래량\t시가\t고가\t저가\tPER', '한화투자증권\t4,400\t1,015\t+29.99%\t60,124,642\t3,800\t4,400\t3,795\t-19.64', '한화투자증권우\t13,330\t3,070\t+29.92%\t201,373\t13,000\t13,330\t13,000\t-59.51']
parsed_data = []

parsed_data.append(stock_datas[0])
for i in range(len(stocks)):
    tmp_stock = stock_datas([i+1])
    tmp_gpt = gpt_datas([i+1])
    parsed_data.append(tmp_stock)
    parsed_data.append(tmp_gpt)
parsed_data = '\n'.join(parsed_data)
print(parsed_data)