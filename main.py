

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

# Import local modules
from models import User, engine
from main_kospi import *
from main_crypto import *
from utils import *

# 비밀번호 해싱을 위한 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")  # 세션 미들웨어 추가

templates = Jinja2Templates(directory="templates")
set_templates(templates)  # templates 객체를 외부로 전달

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
set_db(SessionLocal)

kospi_router = get_kospi_router()
app.include_router(kospi_router)

crypto_router = get_crypto_router()
app.include_router(crypto_router)
# Create static directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    print(f"Created static directory: {static_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
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


