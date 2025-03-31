import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict

def install_requirements():
    required_packages = [
        'fastapi',
        'uvicorn',
        'jinja2',
        'plotly',
        'pandas',
        'yfinance',
        'requests',
        'sqlalchemy',
        'passlib',
        'starlette',
        'itsdangerous'
    ]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"{package} installed successfully!")

# Install required packages first
install_requirements()

# Now import all required packages after installation
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

# Import local modules
from models import User, engine

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")  # 세션 미들웨어 추가

templates = Jinja2Templates(directory="templates")

# Create static directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created static directory: {static_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

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
        # CSV 파일 읽기 (첫 번째 행이 실제 데이터인 경우를 대비)
        df = pd.read_csv('datas/mvrv/mvrv_zscore.csv', header=None)
        
        # 두 개의 열을 'timestamp', 'mvrv_zscore'로 이름 설정
        if df.shape[1] == 2:
            df.columns = ['timestamp', 'mvrv_zscore']
        else:
            raise ValueError("CSV 파일에 두 개의 열이 없습니다.")

        print('Raw DataFrame:', df.head())

        # timestamp 열을 datetime 형식으로 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # 변환 실패한 행 제거
        df = df.dropna(subset=['timestamp'])

        # timestamp를 인덱스로 설정
        df.set_index('timestamp', inplace=True)

        # mvrv_zscore 열 이름 변경
        df = df.rename(columns={'mvrv_zscore': 'Z-Score'})

        print('Processed DataFrame:', df.head())

        return df

    except Exception as e:
        print(f"Error reading MVRV Z-Score data: {e}")
        return pd.DataFrame({'Z-Score': []})

# Initialize data
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

def create_multi_crypto_chart(selected_cryptos, show_mvrv=False):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Color mapping for each cryptocurrency
    colors = {
        'bitcoin': '#F7931A',  # Bitcoin orange
        'ethereum': '#627EEA',  # Ethereum blue
        'ripple': '#23292F'    # Ripple dark
    }
    
    # Add trace for each selected cryptocurrency
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
    
    # Add MVRV Z-Score if enabled
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
    
    # Update layout
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

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """기본 페이지를 /crypto/bitcoin으로 리다이렉트합니다."""
    return RedirectResponse(url="/crypto/bitcoin")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "message": ""}
    )

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "message": "Invalid username or password"}
        )
    
    # 로그인 성공
    user.last_login = datetime.utcnow()
    db.commit()
    
    request.session['user'] = {
        'username': user.username,
        'name': user.name
    }
    return RedirectResponse(url='/', status_code=303)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "message": ""}
    )

@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    # 사용자 이름 중복 체크
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "message": "Username or email already exists"}
        )
    
    # 새 사용자 생성
    hashed_password = pwd_context.hash(password)
    user = User(
        username=username,
        email=email,
        password=hashed_password,
        name=name
    )
    db.add(user)
    db.commit()
    
    return RedirectResponse(url='/login', status_code=303)

@app.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@app.get("/crypto")
async def crypto_redirect():
    """기본 암호화폐 페이지를 /crypto/bitcoin으로 리다이렉트합니다."""
    return RedirectResponse(url="/crypto/bitcoin")

@app.get("/crypto/{cryptos}", response_class=HTMLResponse)
async def crypto_page(request: Request, cryptos: str, mvrv: bool = False, db: Session = Depends(get_db)):
    user = None
    if 'user' in request.session:
        username = request.session['user']['username']
        user = db.query(User).filter(User.username == username).first()
    
    selected_cryptos = cryptos.split(',')
    if not selected_cryptos:
        selected_cryptos = ['bitcoin']
    
    chart = create_multi_crypto_chart(selected_cryptos, show_mvrv=mvrv)
    return templates.TemplateResponse(
        "crypto.html",
        {"request": request, "chart": chart, "user": user}
    )

def get_stock_data(code):
    """KOSPI 종목의 주가 데이터를 가져옵니다."""
    try:
        # 종목 코드를 6자리로 맞추기
        code = str(code).zfill(6)
        # 종목 코드에 .KS 추가 (KOSPI 종목)
        symbol = f"{code}.KS"
        
        # yfinance Ticker 객체 생성
        ticker = yf.Ticker(symbol)
        
        # 데이터 다운로드
        data = ticker.history(start='2010-01-01', end=datetime.now().strftime('%Y-%m-%d'))
        print('data', data)
        
        if data.empty:
            print(f"No data found for {symbol}")
            return pd.DataFrame()
            
        print(f"Data retrieved for {symbol}: {len(data)} rows")
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

@app.get("/kospi")
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

@app.get("/kospi/search")
async def search_kospi(query: str):
    """KOSPI 종목을 검색합니다."""
    query = query.lower()
    results = [
        stock for stock in KOSPI_STOCKS
        if query in stock["name"].lower() or query in stock["code"]
    ]
    return results[:10]  # 최대 10개 결과 반환

@app.get("/kospi/chart/{code}")
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

if __name__ == "__main__":
    # 데이터 디렉토리가 없으면 생성
    if not os.path.exists('datas/crypto'):
        os.makedirs('datas/crypto')
    
    # 암호화폐 데이터가 없으면 다운로드
    cryptos = ['bitcoin', 'ethereum', 'ripple']
    need_download = False
    for crypto in cryptos:
        if not os.path.exists(f'datas/crypto/{crypto}.csv'):
            need_download = True
            break
    
    if need_download:
        print("Downloading cryptocurrency data...")
        from download_crypto_data import download_crypto_data
        download_crypto_data()
        print("Download complete!")
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


