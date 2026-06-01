import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn

from . import database as db
from .scheduler import start_scheduler, check_article
from .scraper import scrape_price, scrape_image

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

PORT = int(os.getenv("APP_PORT", "8462"))
HOST = os.getenv("APP_HOST", "0.0.0.0")
CURRENCY = os.getenv("CURRENCY", "EUR")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    logger.info("Base de données initialisée")
    scheduler = start_scheduler()
    app.state.scheduler = scheduler
    yield
    scheduler.shutdown()


app = FastAPI(title="Price Tracker", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class ArticleIn(BaseModel):
    name: str
    url: str
    css_selector: str
    target_price: Optional[float] = None
    image_selector: Optional[str] = None


class ArticleUpdate(BaseModel):
    name: str
    url: str
    css_selector: str
    target_price: Optional[float] = None
    active: bool = True
    image_selector: Optional[str] = None
    image_url: Optional[str] = None


class PurchasedIn(BaseModel):
    purchased: bool


@app.get("/")
async def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/config")
async def get_config():
    return {"currency": CURRENCY}


@app.get("/api/articles")
async def api_list():
    return db.list_articles()


@app.post("/api/articles")
async def api_add(article: ArticleIn):
    aid = db.add_article(article.name, article.url, article.css_selector,
                         article.target_price, article.image_selector)
    img = await scrape_image(article.url, article.image_selector)
    if img:
        db.set_image_url(aid, img)
    return {"id": aid, "image_url": img}


@app.put("/api/articles/{article_id}")
async def api_update(article_id: int, article: ArticleUpdate):
    if not db.get_article(article_id):
        raise HTTPException(404)
    db.update_article(article_id, article.name, article.url, article.css_selector,
                      article.target_price, article.active,
                      article.image_selector, article.image_url)
    return {"ok": True}


@app.delete("/api/articles/{article_id}")
async def api_delete(article_id: int):
    db.delete_article(article_id)
    return {"ok": True}


@app.post("/api/articles/{article_id}/purchased")
async def api_set_purchased(article_id: int, body: PurchasedIn):
    if not db.get_article(article_id):
        raise HTTPException(404)
    db.set_purchased(article_id, body.purchased)
    return {"ok": True, "purchased": body.purchased}


@app.get("/api/articles/{article_id}/history")
async def api_history(article_id: int, limit: int = 100):
    return db.get_history(article_id, limit)


@app.post("/api/articles/{article_id}/check")
async def api_check_now(article_id: int):
    art = db.get_article(article_id)
    if not art:
        raise HTTPException(404)
    await check_article(art)
    return {"ok": True}


@app.post("/api/articles/{article_id}/refresh-image")
async def api_refresh_image(article_id: int):
    art = db.get_article(article_id)
    if not art:
        raise HTTPException(404)
    img = await scrape_image(art["url"], art.get("image_selector"))
    if img:
        db.set_image_url(article_id, img)
    return {"image_url": img}


@app.post("/api/test-scrape")
async def api_test_scrape(article: ArticleIn):
    price, raw, error = await scrape_price(article.url, article.css_selector)
    img = await scrape_image(article.url, article.image_selector)
    return {"price": price, "raw_text": raw, "error": error, "image_url": img}


@app.get("/api/summary")
async def api_summary():
    arts = db.list_articles()
    # Total = somme des last_price des articles NON achetés
    remaining = [a for a in arts if not a.get("purchased") and a.get("last_price")]
    purchased = [a for a in arts if a.get("purchased") and a.get("last_price")]
    total_remaining = sum(a["last_price"] for a in remaining)
    total_purchased = sum(a["last_price"] for a in purchased)
    return {
        "count": len(arts),
        "count_purchased": sum(1 for a in arts if a.get("purchased")),
        "total_estimated": round(total_remaining, 2),
        "total_purchased": round(total_purchased, 2),
        "currency": CURRENCY
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, log_level="info")
