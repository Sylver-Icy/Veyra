from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

import models.users_model

load_dotenv("veyra.env")
TOKEN = os.getenv("ENGINE")

engine = create_engine(TOKEN)

Session = sessionmaker(bind=engine)

