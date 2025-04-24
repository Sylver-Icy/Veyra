from models.users_model import User
from database.sessionmaker import Session

exp_list = [
    0,100, 250, 400, 600, 900, 1250, 1600, 2200, 3000, 4200, 
    5500, 7000, 9000, 12000, 15000, 18000, 22000, 27000, 
    32000, 38000, 48000, 60000, 78000, 100000
]

def add_exp(user_id: int, exp_amount: int):
    with Session() as session:
        user = session.get(User, user_id)
        user.exp += exp_amount
        current_level=user.level
        new_level= calculate_level(user.exp)
        if new_level>current_level:
            user.level=new_level
            session.commit()
            return new_level
        
        session.commit()

def calculate_level(exp: int) -> int:
    current_level = 0
    for threshold in exp_list:
        if exp >= threshold:
            current_level += 1
        else:
            break
    return current_level      
