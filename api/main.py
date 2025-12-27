# api/main.py
from fastapi import FastAPI
from api.routes import economy, inventory, profile

app = FastAPI(title="Veyra API")

app.include_router(economy.router)
app.include_router(inventory.router)
app.include_router(profile.router)