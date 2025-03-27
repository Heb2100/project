import subprocess
import sys
from datetime import datetime, timedelta
import requests
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from models import User, engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import os
import logging
from typing import List, Dict

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
app.mount("/static", StaticFiles(directory="static"), name="static")

def install_requirements():
    required_packages = ['fastapi', 'uvicorn', 'jinja2', 'plotly', 'pandas', 'yfinance', 'requests', 'sqlalchemy', 'passlib']
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
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

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

def create_stock_chart(data, stock_name, stock_code):
    """주식 차트를 생성합니다."""
    if data.empty:
        return "<div>데이터를 불러올 수 없습니다.</div>"

    # 서브플롯 생성
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price', 'Volume'),
        row_width=[0.7, 0.3]
    )

    # 캔들스틱 차트 추가
    print('data', data['Open'])
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )

    # 거래량 차트 추가
    fig.add_trace(
        go.Bar(
            x=list(data.index),
            y=list(data['Volume']),
            name='Volume',
            marker_color='rgba(0,0,0,0.2)'
        ),
        row=2, col=1
    )

    # 레이아웃 설정
    fig.update_layout(
        title=f"{stock_name} ({stock_code})",
        yaxis_title="Price (KRW)",
        xaxis_title="Date",
        template='plotly_white',
        height=800,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99
        ),
        margin=dict(t=50, l=50, r=50, b=50)
    )

    # Y축 설정
    fig.update_yaxes(title_text="Price (KRW)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)

    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        config={
            'displayModeBar': True,
            'scrollZoom': True,
            'responsive': True
        }
    )

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
    
    return templates.TemplateResponse(
        "kospi.html",
        {"request": request, "chart": "", "user": user}
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
    chart = create_stock_chart(data, stock_info["name"], code)
    
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


