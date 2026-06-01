import os
import requests
import logging

logger = logging.getLogger(__name__)

ENABLED = os.getenv("NTFY_ENABLED", "false").lower() == "true"
URL = os.getenv("NTFY_URL", "https://ntfy.sh").rstrip("/")
TOPIC = os.getenv("NTFY_TOPIC", "")
PRIORITY = os.getenv("NTFY_PRIORITY", "default")


def notify(title: str, message: str, tags: str = "tada"):
    if not ENABLED or not TOPIC:
        return
    try:
        requests.post(
            f"{URL}/{TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": PRIORITY,
                "Tags": tags,
            },
            timeout=10
        )
    except Exception as e:
        logger.warning(f"Erreur ntfy: {e}")
