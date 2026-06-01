import os
import sqlite3
from contextlib import contextmanager
from typing import Optional

DB_PATH = os.getenv("DB_PATH", "/data/tracker.db")

@contextmanager
def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    with get_conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                css_selector TEXT NOT NULL,
                target_price REAL,
                last_price REAL,
                last_checked TEXT,
                active INTEGER DEFAULT 1,
                image_url TEXT,
                image_selector TEXT,
                purchased INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                price REAL,
                raw_text TEXT,
                success INTEGER DEFAULT 1,
                error TEXT,
                checked_at TEXT NOT NULL,
                FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
            )
        """)
        # Migration articles
        cols = {row["name"] for row in c.execute("PRAGMA table_info(articles)").fetchall()}
        if "last_checked" not in cols:
            if "last_check" in cols:
                c.execute("ALTER TABLE articles RENAME COLUMN last_check TO last_checked")
            else:
                c.execute("ALTER TABLE articles ADD COLUMN last_checked TEXT")
        if "image_url" not in cols:
            c.execute("ALTER TABLE articles ADD COLUMN image_url TEXT")
        if "image_selector" not in cols:
            c.execute("ALTER TABLE articles ADD COLUMN image_selector TEXT")
        if "purchased" not in cols:
            c.execute("ALTER TABLE articles ADD COLUMN purchased INTEGER DEFAULT 0")
        # Migration price_history
        hcols = {row["name"] for row in c.execute("PRAGMA table_info(price_history)").fetchall()}
        if "raw_text" not in hcols:
            c.execute("ALTER TABLE price_history ADD COLUMN raw_text TEXT")
        if "success" not in hcols:
            c.execute("ALTER TABLE price_history ADD COLUMN success INTEGER DEFAULT 1")
        if "error" not in hcols:
            c.execute("ALTER TABLE price_history ADD COLUMN error TEXT")


def add_article(name, url, css_selector, target_price=None, image_selector=None):
    with get_conn() as c:
        cur = c.execute(
            "INSERT INTO articles (name, url, css_selector, target_price, image_selector) VALUES (?,?,?,?,?)",
            (name, url, css_selector, target_price, image_selector)
        )
        return cur.lastrowid

def update_article(article_id, name, url, css_selector, target_price, active,
                   image_selector=None, image_url=None):
    with get_conn() as c:
        c.execute("""
            UPDATE articles
            SET name=?, url=?, css_selector=?, target_price=?, active=?,
                image_selector=?, image_url=COALESCE(?, image_url)
            WHERE id=?
        """, (name, url, css_selector, target_price, 1 if active else 0,
              image_selector, image_url, article_id))

def set_image_url(article_id: int, image_url: Optional[str]):
    with get_conn() as c:
        c.execute("UPDATE articles SET image_url=? WHERE id=?", (image_url, article_id))

def set_purchased(article_id: int, purchased: bool):
    with get_conn() as c:
        c.execute("UPDATE articles SET purchased=? WHERE id=?",
                  (1 if purchased else 0, article_id))

def delete_article(article_id):
    with get_conn() as c:
        c.execute("DELETE FROM price_history WHERE article_id=?", (article_id,))
        c.execute("DELETE FROM articles WHERE id=?", (article_id,))

def list_articles():
    with get_conn() as c:
        rows = c.execute("SELECT * FROM articles ORDER BY id").fetchall()
        return [dict(r) for r in rows]

def get_article(article_id):
    with get_conn() as c:
        r = c.execute("SELECT * FROM articles WHERE id=?", (article_id,)).fetchone()
        return dict(r) if r else None

def update_price(article_id, price, checked_at):
    with get_conn() as c:
        c.execute(
            "UPDATE articles SET last_price=?, last_checked=? WHERE id=?",
            (price, checked_at, article_id)
        )

def add_history(article_id, price, raw_text=None, success=True, error=None):
    from datetime import datetime
    checked_at = datetime.utcnow().isoformat()
    with get_conn() as c:
        c.execute(
            """INSERT INTO price_history
               (article_id, price, raw_text, success, error, checked_at)
               VALUES (?,?,?,?,?,?)""",
            (article_id, price, raw_text, 1 if success else 0, error, checked_at)
        )
        if success and price is not None:
            c.execute(
                "UPDATE articles SET last_price=?, last_checked=? WHERE id=?",
                (price, checked_at, article_id)
            )
        else:
            c.execute(
                "UPDATE articles SET last_checked=? WHERE id=?",
                (checked_at, article_id)
            )

def get_history(article_id, limit=100):
    with get_conn() as c:
        rows = c.execute(
            """SELECT price, raw_text, success, error, checked_at
               FROM price_history WHERE article_id=?
               ORDER BY id DESC LIMIT ?""",
            (article_id, limit)
        ).fetchall()
        return [dict(r) for r in rows]

def get_last_successful_price(article_id: int) -> Optional[float]:
    with get_conn() as c:
        r = c.execute(
            """SELECT price FROM price_history
               WHERE article_id=? AND success=1 AND price IS NOT NULL
               ORDER BY id DESC LIMIT 1""",
            (article_id,)
        ).fetchone()
        return r["price"] if r else None
