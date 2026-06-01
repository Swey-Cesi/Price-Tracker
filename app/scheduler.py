import os
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from . import database as db
from .scraper import scrape_price
from .notifier import notify

logger = logging.getLogger(__name__)

INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "1"))
CURRENCY = os.getenv("CURRENCY", "EUR")


async def check_article(article):
    aid = article["id"]
    logger.info(f"Vérification : {article['name']}")
    previous = db.get_last_successful_price(aid)
    price, raw, error = await scrape_price(article["url"], article["css_selector"])
    success = price is not None
    db.add_history(aid, price, raw, success, error)

    if success:
        # Notification si baisse
        if previous is not None and price < previous:
            notify(
                title=f"📉 Baisse de prix : {article['name']}",
                message=f"{previous:.2f} {CURRENCY} → {price:.2f} {CURRENCY}\n{article['url']}",
                tags="chart_with_downwards_trend"
            )
        # Notification si prix cible atteint
        if article.get("target_price") and price <= article["target_price"]:
            notify(
                title=f"🎯 Prix cible atteint : {article['name']}",
                message=f"Prix actuel : {price:.2f} {CURRENCY} (cible : {article['target_price']:.2f})\n{article['url']}",
                tags="dart"
            )


async def run_all_checks():
    articles = [a for a in db.list_articles() if a["active"]]
    for art in articles:
        try:
            await check_article(art)
        except Exception as e:
            logger.exception(f"Erreur check {art['id']}: {e}")
        await asyncio.sleep(2)


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_all_checks, "interval", hours=INTERVAL_HOURS, id="check_prices", next_run_time=None)
    scheduler.start()
    logger.info(f"Scheduler démarré (toutes les {INTERVAL_HOURS}h)")
    return scheduler
