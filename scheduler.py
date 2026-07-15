from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


def add_daily_job(func, hour, minute):
    scheduler.add_job(
        func,
        trigger="cron",
        hour=hour,
        minute=minute,
        replace_existing=True
    )


def start_scheduler():
    scheduler.start()
