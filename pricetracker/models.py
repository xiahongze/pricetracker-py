"""SQL Schemas -- ORM with sqlalchemy
"""
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator, TypeVar

from pydantic import Field, create_model
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm.session import Session as SessionType
from sqlalchemy.orm.session import sessionmaker

from pricetracker.config import config

Base = declarative_base()


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    po_user = Column(String, nullable=False)
    po_device = Column(String, default="")
    pages = relationship(
        "PageORM", back_populates="user", cascade="all, delete, delete-orphan"
    )


class WebsiteConfigORM(Base):
    __tablename__ = "website_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    xpath = Column(String, nullable=False)
    pages = relationship(
        "PageORM", back_populates="config", cascade="all, delete, delete-orphan"
    )
    active = Column(Boolean, default=True)


class PageORM(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)
    next_check = Column(DateTime, default=datetime.now)
    freq = Column(Integer, default=24)  # hours
    retry = Column(Integer, default=0)  # counter
    active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("UserORM", back_populates="pages")

    config_id = Column(Integer, ForeignKey("website_config.id"), nullable=False)
    config = relationship("WebsiteConfigORM", back_populates="pages")

    prices = relationship(
        "PriceORM", back_populates="page", cascade="all, delete, delete-orphan"
    )


class PriceORM(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    price = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)

    page_id = Column(Integer, ForeignKey("pages.id"))
    page = relationship("PageORM", back_populates="prices")


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

ModelTypeBoundOrm = TypeVar(
    "ModelTypeBoundOrm", UserORM, WebsiteConfigORM, PageORM, PriceORM
)


class PydanticConfigObject:
    orm_mode = True


def convert_sqlalchemy_model(model: ModelTypeBoundOrm, model_name: str):
    """convert_sqlalchemy_model converts sqlalchemy model to pydantic model"""
    fields = {}
    for column in model.__table__.columns:
        column: Column
        if column.nullable or column.default is not None or column.name == "id":
            # nullable, default, primary key
            # primary key is nullable because when we post to create an entity,
            # we don't have the id yet so we can't set it
            if column.default and callable(column.default.arg):
                # default is a callable, e.g. datetime.now
                # note that it is wrapped in a function that expects a ctx var
                # plus args so we need to unwrap it
                fields[column.name] = (
                    column.type.python_type,
                    Field(default_factory=column.default.arg.__wrapped__),
                )
            else:
                fields[column.name] = (
                    column.type.python_type,
                    Field(default=column.default.arg if column.default else None),
                )
        else:
            fields[column.name] = (column.type.python_type, ...)
    return create_model(model_name, **fields, __config__=PydanticConfigObject)


User = convert_sqlalchemy_model(UserORM, "User")
WebsiteConfig = convert_sqlalchemy_model(WebsiteConfigORM, "WebsiteConfig")
Page = convert_sqlalchemy_model(PageORM, "Page")
Price = convert_sqlalchemy_model(PriceORM, "Price")

ModelTypeBoundPy = TypeVar("ModelTypeBoundPy", User, WebsiteConfig, Page, Price)
