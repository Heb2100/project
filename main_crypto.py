import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session, sessionmaker
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from passlib.context import CryptContext

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional
from models import User
from main import *
from utils import *


app = None  # 외부에서 주입 받을 변수
crypto_router = get_crypto_router()

def get_crypto_data(symbol: str) -> pd.Series:
    """
    암호화폐 데이터를 로컬 CSV 파일에서 읽어옵니다.
    """
    try:
        # CSV 파일에서 데이터 읽기
        filename = f'datas/crypto/{symbol}.csv'
        if not os.path.exists(filename):
            logging.error(f"Data file not found for {symbol}")
            return pd.Series()
        
        data = pd.read_csv(filename, index_col=0, parse_dates=True)
        data.index = pd.to_datetime(data.index)
        
        logging.info(f"Successfully loaded {symbol} data from {filename}")
        logging.info(f"Data range: {data.index[0]} to {data.index[-1]}")
        
        return data

    except Exception as e:
        logging.error(f"Error loading {symbol} data: {e}")
        return pd.Series()

def get_multi_crypto_data(symbols: List[str], show_mvrv: bool = False) -> Dict[str, pd.Series]:
    """
    여러 암호화폐의 데이터를 가져옵니다.
    """
    result = {}
    for symbol in symbols:
        data = get_crypto_data(symbol)
        if not data.empty:
            result[symbol] = data
    
    if show_mvrv and 'bitcoin' in symbols:
        try:
            mvrv_data = pd.read_csv('datas/mvrv.csv', index_col=0, parse_dates=True)
            mvrv_data.index = pd.to_datetime(mvrv_data.index)
            result['mvrv'] = mvrv_data['mvrv_z_score']
        except Exception as e:
            logging.error(f"Error loading MVRV data: {e}")
    
    return result

def get_mvrv_data():
    try:
        df = pd.read_csv('datas/mvrv/mvrv_zscore.csv', header=None)
        if df.shape[1] == 2:
            df.columns = ['timestamp', 'mvrv_zscore']
        else:
            raise ValueError("CSV 파일에 두 개의 열이 없습니다.")
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df.set_index('timestamp', inplace=True)
        df = df.rename(columns={'mvrv_zscore': 'Z-Score'})
        return df
    except Exception as e:
        print(f"Error reading MVRV Z-Score data: {e}")
        return pd.DataFrame({'Z-Score': []})

def initialize_crypto_data():
    result = {}
    cryptos = ['bitcoin', 'ethereum', 'ripple']
    for crypto in cryptos:
        data = get_crypto_data(crypto)
        if not isinstance(data.empty, bool):  # Series인 경우
            data = pd.DataFrame(data)
            data.columns = ['Close']
        if not data.empty:
            data = data[data['Close'] > 0]  # 0보다 큰 값만 유지
            data = data.dropna()  # NA 값 제거
            result[crypto] = data
    return result

# Global variables
crypto_data = initialize_crypto_data()
mvrv_data = get_mvrv_data()

def create_multi_crypto_chart(selected_cryptos, show_mvrv=False, crypto_data=None, mvrv_data=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = {
        'bitcoin': '#F7931A',  # Bitcoin orange
        'ethereum': '#627EEA',  # Ethereum blue
        'ripple': '#23292F'    # Ripple dark
    }
    for crypto_name in selected_cryptos:
        if crypto_name in crypto_data:
            data = crypto_data[crypto_name]
            display_name = crypto_name.capitalize()
            
            fig.add_trace(
                go.Scatter(
                    x=list(data.index),
                    y=list(data['Close']),
                    mode='lines',
                    name=f"{display_name} Price",
                    line=dict(color=colors.get(crypto_name, 'black'), width=2)
                ),
                secondary_y=False
            )
    if show_mvrv:
        fig.add_trace(
            go.Scatter(
                x=list(mvrv_data.index),
                y=list(mvrv_data['Z-Score']),
                mode='lines',
                name='MVRV Z-Score',
                line=dict(color='#FF0000', width=2)
            ),
            secondary_y=True
        )
    fig.update_layout(
        title={
            'text': 'Cryptocurrency Prices & MVRV Z-Score',
            'x': 0.05,
            'xanchor': 'left',
            'font': dict(size=20)
        },
        template='plotly_white',
        height=600,
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    # Update yaxis properties
    fig.update_yaxes(
        title_text="Price (USD)",
        type="log",
        tickformat="$,.0f",
        showgrid=True,
        gridcolor='lightgrey',
        tickprefix="$",
        secondary_y=False
    )

    # Update secondary yaxis properties
    if show_mvrv:
        fig.update_yaxes(
            title_text="MVRV Z-Score",
            showgrid=False,
            secondary_y=True,
            tickformat=".2f"
        )
    
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id="chart",
        config={
            'displayModeBar': True,
            'scrollZoom': True,
            'responsive': True
        }
    )


@crypto_router.get("/crypto", response_class=HTMLResponse)
async def crypto_page(
    request: Request,
    bitcoin: bool = False,
    ethereum: bool = False,
    ripple: bool = False,
    mvrv: bool = False,
    db: Session = Depends(get_db)
):
    templates = get_templates()  # 외부에서 주입될 예정
    user = None
    if 'user' in request.session:
        username = request.session['user']['username']
        user = db.query(User).filter(User.username == username).first()
    
    # 데이터 초기화를 함수 내부로 이동
    crypto_data = initialize_crypto_data()
    mvrv_data = get_mvrv_data()
    
    # 선택된 암호화폐 목록 생성
    selected_cryptos = []
    if bitcoin:
        selected_cryptos.append('bitcoin')
    if ethereum:
        selected_cryptos.append('ethereum')
    if ripple:
        selected_cryptos.append('ripple')
    
    # 아무것도 선택되지 않았다면 bitcoin을 기본값으로
    if not selected_cryptos:
        selected_cryptos = ['bitcoin']
    
    # create_multi_crypto_chart 함수에 데이터 전달
    chart = create_multi_crypto_chart(selected_cryptos, show_mvrv=mvrv, crypto_data=crypto_data, mvrv_data=mvrv_data)
    return templates.TemplateResponse(
        "crypto.html",
        {
            "request": request,
            "chart": chart,
            "user": user,
            "selected_cryptos": {
                "bitcoin": bitcoin,
                "ethereum": ethereum,
                "ripple": ripple,
                "mvrv": mvrv
            }
        }
    )