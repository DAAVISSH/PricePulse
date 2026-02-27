import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_price_alert(product_name: str, previous_price: float, current_price: float):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return

    change = round(current_price - previous_price, 2)
    change_percent = round((change / previous_price) * 100, 2)
    direction = "📉 Price Drop" if change < 0 else "📈 Price Increase"

    message = (
        f"{direction}\n\n"
        f"🖥 {product_name}\n"
        f"Previous: €{previous_price}\n"
        f"Current: €{current_price}\n"
        f"Change: €{change} ({change_percent}%)"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    httpx.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})

def send_price_alert(product_name: str, previous_price: float, current_price: float):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Missing token or chat ID")
        return

    change = round(current_price - previous_price, 2)
    change_percent = round((change / previous_price) * 100, 2)
    direction = "📉 Price Drop" if change < 0 else "📈 Price Increase"

    message = (
        f"{direction}\n\n"
        f"🖥 {product_name}\n"
        f"Previous: €{previous_price}\n"
        f"Current: €{current_price}\n"
        f"Change: €{change} ({change_percent}%)"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = httpx.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    print(f"Telegram response: {response.status_code} - {response.text}")