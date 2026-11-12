from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main.api.configs.config import Config



engine = create_engine(url=Config.fetch("databaseUrl"), echo=False)
SessionLocal = sessionmaker(bind=engine)
