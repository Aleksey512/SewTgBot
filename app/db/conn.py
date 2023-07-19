import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE = os.getenv('DATABASE')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

engine = create_engine(
    f"{DATABASE}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}", echo=True)


class Base(DeclarativeBase):
    pass


Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
session = Session()


def init_models():
    Base.metadata.create_all(engine)
