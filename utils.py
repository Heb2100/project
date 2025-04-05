from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import sessionmaker, Session
from fastapi import APIRouter, Request, Depends

templates = None
SessionLocal = None
kospi_router = APIRouter()  # 여기서 생성
crypto_router = APIRouter()  # 여기서 생성

def set_templates(t: Jinja2Templates):
    global templates
    templates = t

def get_templates() -> Jinja2Templates:
    return templates

def set_db(session_factory):
    global SessionLocal
    SessionLocal = session_factory

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_kospi_router() -> APIRouter:
    return kospi_router
        
def get_crypto_router() -> APIRouter:
    return crypto_router