from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

import models.users_model

load_dotenv("veyra.env")
DB_URL = os.getenv("ENGINE")

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)
