import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session
from dotenv import load_dotenv

class Base(DeclarativeBase):
    pass

SessionLocal = None
engine = None

def init_db(app=None):
    load_dotenv()
    global SessionLocal, engine
    user = os.getenv("DB_USER")
    pwd  = os.getenv("DB_PASS")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME")
    uri = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{name}?charset=utf8mb4"
    engine = create_engine(uri, echo=False, pool_pre_ping=True)
    SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_session():
    return SessionLocal()

db = Base
