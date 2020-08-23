from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __table_name__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    po_user = Column(String, nullable=False)
    po_token = Column(String, nullable=False)


class WebsiteConfig(Base):
    __table_name__ = 'website_config'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    regex = Column(String, nullable=False)
    use_driver = Column(Boolean, default=False)


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
