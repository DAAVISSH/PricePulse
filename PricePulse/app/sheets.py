import gspread
from google.oauth2.service_account import Credentials
from app.models import Product, PriceHistory
from app.database import SessionLocal
import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CREDENTIALS_FILE = "credentials.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_sheet():
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet.sheet1

def sync_to_sheets():
    db = SessionLocal()
    try:
        sheet = get_sheet()
        sheet.clear()
        sheet.append_row(["Product", "URL", "Previous Price", "Latest Price", "Change", "Last Scraped"])

        products = db.query(Product).all()
        for product in products:
            history = db.query(PriceHistory).filter(
                PriceHistory.product_id == product.id
            ).order_by(PriceHistory.scraped_at.desc()).limit(2).all()

            if not history:
                continue

            latest_price = f"€{history[0].price}"
            last_scraped = str(history[0].scraped_at)

            if len(history) == 2:
                previous_price = f"€{history[1].price}"
                change = round(history[0].price - history[1].price, 2)
                change_str = f"€{change}" if change != 0 else "No change"
            else:
                previous_price = "First entry"
                change_str = "-"

            sheet.append_row([
                product.name or "Unknown",
                product.url,
                previous_price,
                latest_price,
                change_str,
                last_scraped
            ])
    finally:
        db.close()