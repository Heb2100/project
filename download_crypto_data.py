import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def download_crypto_data():
    # 데이터를 저장할 디렉토리 생성
    if not os.path.exists('datas/crypto'):
        os.makedirs('datas/crypto')
    
    # 다운로드할 암호화폐 목록
    cryptos = {
        'bitcoin': 'BTC-USD',
        'ethereum': 'ETH-USD',
        'ripple': 'XRP-USD'
    }
    
    start_date = '2010-01-01'
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    for name, symbol in cryptos.items():
        print(f"Downloading {name} data...")
        try:
            # yfinance를 사용하여 데이터 다운로드
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            
            # 종가만 저장
            close_data = data['Close']
            
            # CSV 파일로 저장
            filename = f'datas/crypto/{name}.csv'
            close_data.to_csv(filename)
            print(f"Saved {name} data to {filename}")
            
        except Exception as e:
            print(f"Error downloading {name} data: {e}")

if __name__ == "__main__":
    download_crypto_data() 