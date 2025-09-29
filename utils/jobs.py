from apscheduler.schedulers.asyncio import AsyncIOScheduler
from services.shop_services import update_daily_shop,update_daily_buyback_shop
from services.delievry_minigame_services import reset_skips

scheduler = AsyncIOScheduler()
scheduler.add_job(update_daily_shop, 'interval', minutes=5)
scheduler.add_job(update_daily_buyback_shop, 'interval', minutes=5)
scheduler.add_job(reset_skips, 'interval', minutes=5)

def run_at_startup():
    "Runs the functions that need to fill values at bot startup"
    update_daily_buyback_shop()
    update_daily_shop()