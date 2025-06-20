from database.sessionmaker import engine
from models.users_model import Base
import models.inventory_model 

Base.metadata.create_all(engine)
print("All tables created.")
