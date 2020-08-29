"""SQL Schemas -- ORM with sqlalchemy
"""
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session as SessionType
from sqlalchemy.orm.session import sessionmaker

from .config import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    po_user = Column(String, nullable=False)
    po_device = Column(String, default='')
    pages = relationship("Page", back_populates="user", cascade="all, delete, delete-orphan")


class WebsiteConfig(Base):
    __tablename__ = 'website_config'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    xpath = Column(String, nullable=False)
    pages = relationship("Page", back_populates="config", cascade="all, delete, delete-orphan")


class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)
    next_check = Column(DateTime, default=datetime.now)
    freq = Column(Integer, default=24)  # hours
    retry = Column(Integer, default=0)  # counter
    active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="pages")

    config_id = Column(Integer, ForeignKey('website_config.id'), nullable=False)
    config = relationship("WebsiteConfig", back_populates="pages")

    prices = relationship("Price", back_populates="page",
                          cascade="all, delete, delete-orphan")


class Price(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)

    page_id = Column(Integer, ForeignKey('pages.id'))
    page = relationship("Page", back_populates="prices")


engine = create_engine(config.db_path, echo=config.debug)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def create_session() -> Generator[SessionType, Any, None]:
    """Provide a transactional scope around a series of operations.
    https://docs.sqlalchemy.org/en/13/orm/session_basics.html#when-do-i-construct-a-session-when-do-i-commit-it-and-when-do-i-close-it
    """
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


create_session_auto = contextmanager(create_session)
