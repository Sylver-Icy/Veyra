from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from services.shop_services import update_daily_shop, update_daily_buyback_shop
from services.delievry_minigame_services import reset_skips
from services.guessthenumber_services import reset_all_daily
scheduler = AsyncIOScheduler()

# Run every day at 00:00 (midnight)
midnight_trigger = CronTrigger(hour=0, minute=0, timezone=timezone("UTC"))

scheduler.add_job(update_daily_shop, trigger=midnight_trigger)
scheduler.add_job(update_daily_buyback_shop, trigger=midnight_trigger)
scheduler.add_job(reset_skips, trigger=midnight_trigger)
scheduler.add_job(reset_all_daily, trigger=midnight_trigger)

def run_at_startup():
    """Runs the functions that need to fill values at bot startup"""
    update_daily_buyback_shop()
    update_daily_shop()
