import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE = os.getenv('DB')
DATABASE_PATH = os.getenv('DB_PATH')

engine = create_engine(f"{DATABASE}:///{DATABASE_PATH}", echo=True)


class Base(DeclarativeBase):
    pass


Session = scoped_session(sessionmaker(bind=engine, expire_on_commit=False))
session = Session()


def init_models():
    Base.metadata.create_all(engine)
