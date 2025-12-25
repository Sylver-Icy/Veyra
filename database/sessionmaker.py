from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


load_dotenv("veyra.env")
DB_URL = os.getenv("DB_URL")
TEST_DB_URL = os.getenv("TEST_DB_URL")

engine = create_engine(DB_URL)
# For testing purposes, you can switch to TEST_DB_URL
# engine = create_engine(TEST_DB_URL)

Session = sessionmaker(bind=engine)



