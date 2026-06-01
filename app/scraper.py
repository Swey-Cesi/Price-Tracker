import logging
import re
from urllib.parse import urljoin
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


async def _new_page(p):
    browser = await p.chromium.launch(args=["--no-sandbox"])
    ctx = await browser.new_context(user_agent=USER_AGENT, locale="fr-FR")
    page = await ctx.new_page()
    return browser, ctx, page


async def scrape_price(url: str, css_selector: str):
    """Retourne (price: float|None, raw_text: str|None, error: str|None)"""
    try:
        async with async_playwright() as p:
            browser, ctx, page = await _new_page(p)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1500)
                el = await page.query_selector(css_selector)
                if not el:
                    snippet = (await page.content())[:500]
                    return None, None, f"Sélecteur introuvable : {css_selector}. Début page : {snippet}"
                raw = (await el.inner_text()).strip()
                price = _parse_price(raw)
                return price, raw, None
            finally:
                try:
                    await ctx.close()
                except Exception:
                    pass
                try:
                    await browser.close()
                except Exception:
                    pass
    except Exception as e:
        logger.error("Erreur scraping", exc_info=True)
        return None, None, str(e)


async def scrape_image(url: str, image_selector: str | None = None) -> str | None:
    """
    Tente d'extraire l'URL d'image :
    1. via image_selector si fourni (attribut src/srcset/data-src)
    2. fallback sur meta og:image / twitter:image
    """
    try:
        async with async_playwright() as p:
            browser, ctx, page = await _new_page(p)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1500)

                # 1. Sélecteur dédié
                if image_selector:
                    el = await page.query_selector(image_selector)
                    if el:
                        src = await el.get_attribute("src") or await el.get_attribute("data-src")
                        if not src:
                            srcset = await el.get_attribute("srcset")
                            if srcset:
                                src = srcset.split(",")[0].strip().split(" ")[0]
                        if src:
                            return urljoin(url, src)

                # 2. Fallback meta
                for sel in [
                    'meta[property="og:image"]',
                    'meta[name="og:image"]',
                    'meta[name="twitter:image"]',
                ]:
                    m = await page.query_selector(sel)
                    if m:
                        content = await m.get_attribute("content")
                        if content:
                            return urljoin(url, content)
                return None
            finally:
                try:
                    await ctx.close()
                except Exception:
                    pass
                try:
                    await browser.close()
                except Exception:
                    pass
    except Exception as e:
        logger.warning(f"Erreur scrape_image: {e}")
        return None


def _parse_price(text: str) -> float | None:
    if not text:
        return None
    t = text.replace("\xa0", " ").replace(" ", "")
    m = re.search(r"(\d[\d.,]*)", t)
    if not m:
        return None
    num = m.group(1)
    if "," in num:
        num = num.replace(".", "").replace(",", ".")
    try:
        return float(num)
    except ValueError:
        return None
