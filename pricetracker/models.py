from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import sessionmaker

from pricetracker.config import config

Base = declarative_base()


class User(Base):
    __table_name__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    po_user = Column(String, nullable=False)
    po_device = Column(String, default='')


class WebsiteConfig(Base):
    __table_name__ = 'website_config'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    regex = Column(String, nullable=False)


class Page(Base):
    __table_name__ = 'pages'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)
    updated_time = Column(DateTime, default=datetime.now)
    next_check = Column(DateTime, default=datetime.now)
    retry = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="pages")


class PriceHistory(Base):
    __table_name__ = 'price_history'

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
