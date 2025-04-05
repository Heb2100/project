
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

templates = get_templates()  # 외부에서 주입될 예정
app = None  # 외부에서 주입 받을 변수
kospi_router = get_kospi_router()
    
def get_stock_data(code):
    """KOSPI 종목의 주가 데이터를 가져옵니다."""
    try:
        code = str(code).zfill(6)
        symbol = f"{code}.KS"
        ticker = yf.Ticker(symbol)        
        data = ticker.history(start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))        
        if data.empty:
            return pd.DataFrame()            
        return data
        
    except Exception as e:
        print(f"Error fetching stock data for {code}: {e}")
        return pd.DataFrame()

def create_stock_chart(data: pd.DataFrame, symbol: str) -> str:
    """주식 차트를 생성합니다."""
    if data.empty:
        return "<div>데이터를 불러올 수 없습니다.</div>"

    # 현재가, 전일대비 계산
    current_price = data['Close'].iloc[-1]
    prev_price = data['Close'].iloc[-2]
    price_change = current_price - prev_price
    price_change_percent = (price_change / prev_price) * 100

    # 데이터를 리스트로 변환
    dates = list(data.index)
    opens = list(data['Open'])
    highs = list(data['High'])
    lows = list(data['Low'])
    closes = list(data['Close'])
    volumes = list(data['Volume'])

    # 거래량 색상 설정
    volume_colors = ['rgb(255, 78, 66)' if close >= open_price else 'rgb(51, 103, 204)'
                    for close, open_price in zip(closes, opens)]

    # 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3]
    )

    # 캔들스틱 차트 추가
    fig.add_trace(
        go.Candlestick(
            x=dates,
            open=opens,
            high=highs,
            low=lows,
            close=closes,
            name='OHLC',
            increasing_line_color='rgb(255, 78, 66)',
            decreasing_line_color='rgb(51, 103, 204)'
        ),
        row=1, col=1
    )

    # 거래량 차트 추가
    fig.add_trace(
        go.Bar(
            x=dates,
            y=volumes,
            marker_color=volume_colors,
            name='Volume',
            showlegend=False
        ),
        row=2, col=1
    )

    # 레이아웃 설정
    fig.update_layout(
        title=None,
        height=600,
        showlegend=False,
        margin=dict(t=50, l=50, r=50, b=10),
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_rangeslider_visible=False,
        dragmode='pan'
    )

    # Y축 설정
    fig.update_yaxes(
        title=None,
        row=1, col=1,
        tickformat=",",
        gridcolor='lightgrey',
        showgrid=True,
        side='right',
        fixedrange=False
    )
    fig.update_yaxes(
        title=None,
        row=2, col=1,
        tickformat=",",
        gridcolor='lightgrey',
        showgrid=True,
        side='right',
        fixedrange=True
    )

    # X축 설정
    fig.update_xaxes(
        showticklabels=False,
        gridcolor='lightgrey',
        showgrid=True,
        row=1, col=1,
        rangeslider_visible=False,
        fixedrange=False
    )
    fig.update_xaxes(
        gridcolor='lightgrey',
        showgrid=True,
        row=2, col=1,
        rangeslider_visible=False,
        fixedrange=False
    )

    # 차트를 HTML로 변환
    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs=True,
        config={
            'displayModeBar': False,
            'scrollZoom': True,
            'responsive': True,
            'dragmode': 'pan',
            'modeBarButtonsToRemove': ['zoomIn', 'zoomOut', 'autoScale'],
            'doubleClick': 'reset+autosize',
            'showTips': True,
            'scrollZoomModifier': 'alt'
        }
    )

    # 주식 정보와 차트를 포함한 HTML 생성
    final_html = f"""
    <style>
        .stock-info-container {{
            display: flex;
            justify-content: space-between;
            padding: 20px;
            background-color: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            margin-bottom: 10px;
        }}
        .stock-info-left {{
            flex: 1;
        }}
        .stock-info-right {{
            flex: 1;
            padding-left: 20px;
            border-left: 1px solid #dee2e6;
        }}
        .stock-name-code {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .stock-price {{
            margin-bottom: 10px;
        }}
        .current-price {{
            font-size: 28px;
            font-weight: bold;
            margin-right: 10px;
        }}
        .price-change {{
            font-size: 18px;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .price-change.up {{
            color: #ff4d4d;
            background-color: #ffe6e6;
        }}
        .price-change.down {{
            color: #3366cc;
            background-color: #e6f0ff;
        }}
        .price-details {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
            color: #666;
        }}
        .market-info {{
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .market-info h3 {{
            margin: 0 0 10px 0;
            color: #333;
            font-size: 18px;
        }}
        .market-info p {{
            margin: 0;
            color: #555;
            line-height: 1.5;
        }}
    </style>
    <div class="stock-info-container">
        <div class="stock-info-left">
            <div class="stock-name-code">{symbol}</div>
            <div class="stock-price">
                <span class="current-price">{current_price:,.0f}</span>
                <span class="price-change {price_change >= 0 and 'up' or 'down'}">
                    {price_change >= 0 and '+' or ''}{price_change:,.0f} ({price_change_percent:.2f}%)
                </span>
            </div>
            <div class="price-details">
                <div>고가: {data['High'].iloc[-1]:,.0f}</div>
                <div>저가: {data['Low'].iloc[-1]:,.0f}</div>
                <div>거래량: {data['Volume'].iloc[-1]:,.0f}</div>
            </div>
        </div>
        <div class="stock-info-right">
            <div class="market-info">
                <h3>시장 정보</h3>
                <p>실시간 주가 정보 제공</p>
                <p>거래량 기반 분석</p>
                <p>가격 변동 모니터링</p>
            </div>
        </div>
    </div>
    {chart_html}
    """

    return final_html

# KOSPI 종목 정보 (예시 데이터)
KOSPI_STOCKS = [
    {"code": "005930", "name": "삼성전자"},
    {"code": "000660", "name": "SK하이닉스"},
    {"code": "035420", "name": "NAVER"},
    {"code": "005380", "name": "현대차"},
    {"code": "051910", "name": "LG화학"},
    {"code": "035720", "name": "카카오"},
    {"code": "005490", "name": "POSCO홀딩스"},
    {"code": "055550", "name": "신한지주"},
    {"code": "000270", "name": "기아"},
    {"code": "105560", "name": "KB금융"}
]

@kospi_router.get("/kospi")
async def kospi_page(request: Request, db: Session = Depends(get_db)):
    """KOSPI 페이지를 표시합니다."""
    user = None
    if 'user' in request.session:
        username = request.session['user']['username']
        user = db.query(User).filter(User.username == username).first()
    
    # 삼성전자 기본 표시
    default_stock = next((stock for stock in KOSPI_STOCKS if stock["code"] == "005930"), None)
    data = get_stock_data("005930")
    chart = create_stock_chart(data, default_stock["name"]) if not data.empty else ""
    
    return templates.TemplateResponse(
        "kospi.html",
        {
            "request": request,
            "chart": chart,
            "stock_info": default_stock,
            "user": user
        }
    )

@kospi_router.get("/kospi/search")
async def search_kospi(query: str):
    """KOSPI 종목을 검색합니다."""
    query = query.lower()
    results = [
        stock for stock in KOSPI_STOCKS
        if query in stock["name"].lower() or query in stock["code"]
    ]
    return results[:10]  # 최대 10개 결과 반환

@kospi_router.get("/kospi/chart/{code}")
async def get_kospi_chart(request: Request, code: str, db: Session = Depends(get_db)):
    """특정 KOSPI 종목의 차트를 표시합니다."""
    user = None
    if 'user' in request.session:
        username = request.session['user']['username']
        user = db.query(User).filter(User.username == username).first()
    
    # 종목 정보 찾기
    stock_info = next((stock for stock in KOSPI_STOCKS if stock["code"] == code), None)
    if not stock_info:
        return {"error": "종목을 찾을 수 없습니다."}

    # 주가 데이터 가져오기
    data = get_stock_data(code)
    if data.empty:
        return {"error": "데이터를 불러올 수 없습니다."}

    # 차트 생성
    chart = create_stock_chart(data, stock_info["name"])
    
    return templates.TemplateResponse(
        "kospi.html",
        {
            "request": request,
            "chart": chart,
            "stock_info": stock_info,
            "user": user
        }
    )