from sqlalchemy.engine import create_engine

from .config import Config
from .models import Base as SQLModelBase


def main():
    engine = create_engine(Config.db_path, echo=True)
    SQLModelBase.metadata.create_all(engine)
    pass


if __name__ == "__main__":
    main()
