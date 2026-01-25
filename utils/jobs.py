from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from pytz import timezone

from services.shop_services import update_daily_shop, update_daily_buyback_shop
from services.delievry_minigame_services import reset_skips
from services.guessthenumber_services import reset_all_daily
from services.friendship_services import reset_all_daily_exp
from services.jobs_services import regen_energy_for_all
from services.loan_services import send_due_loan_reminders

from utils.embeds.leaderboard.weeklyleaderboard import send_weekly_leaderboard
from utils.embeds.lottery.sendlottery import send_lottery, send_result

scheduler = AsyncIOScheduler(
    job_defaults={
        "coalesce": True,              # if missed multiple runs -> run once
        "misfire_grace_time": 86400,   # if missed midnight -> still run within 24h
        "max_instances": 1,            # avoid overlapping runs
    }
)

# Run every day at 00:00 (midnight)
midnight_trigger = CronTrigger(hour=0, minute=0, timezone=timezone("UTC"))
# Weekly leaderboard — Sunday 00:00 (UTC)
weekly_trigger = CronTrigger(day_of_week="sun", hour=0, minute=0, timezone=timezone("UTC"))

def schedule_jobs(bot):
    """Registers all recurring background jobs."""
    # Daily jobs
    scheduler.add_job(update_daily_shop, trigger=midnight_trigger)
    scheduler.add_job(update_daily_buyback_shop, trigger=midnight_trigger)
    scheduler.add_job(reset_skips, trigger=midnight_trigger)
    scheduler.add_job(reset_all_daily, trigger=midnight_trigger)
    scheduler.add_job(reset_all_daily_exp, trigger=midnight_trigger)
    scheduler.add_job(send_weekly_leaderboard, trigger=weekly_trigger, args=[bot])
    scheduler.add_job(send_lottery, trigger=CronTrigger(day_of_week="sat,sun", hour=0, minute=0, timezone=timezone("UTC")), args=[bot, 50])
    scheduler.add_job(send_lottery, trigger=CronTrigger(day_of_week="mon-fri", hour=0, minute=0, timezone=timezone("UTC")), args=[bot, 10])
    scheduler.add_job(send_result, trigger=midnight_trigger, args=[bot])
    scheduler.add_job(regen_energy_for_all, trigger=IntervalTrigger(minutes=6, start_date=None), args=[bot])
    scheduler.add_job(send_due_loan_reminders, trigger=midnight_trigger, args=[bot])



async def run_at_startup(bot):
    """Runs the functions that need to fill values at bot startup"""
    update_daily_shop()
    update_daily_buyback_shop()
    await send_lottery(bot, 10)