"""SQL Schemas -- ORM with sqlalchemy
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker

from .config import config

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    po_user = Column(String, nullable=False)
    po_device = Column(String, default='')


class WebsiteConfig(Base):
    __tablename__ = 'website_config'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    regex = Column(String, nullable=False)


class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)
    updated_time = Column(DateTime, default=datetime.now)
    freq = Column(Integer, default=24)  # hours
    retry = Column(Integer, default=0)  # counter
    active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="pages")


class Price(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True)
    price = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)

    page_id = Column(Integer, ForeignKey('pages.id'))
    page = relationship("Page", back_populates="price_history")


engine = create_engine(config.db_path, echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def create_session():
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
