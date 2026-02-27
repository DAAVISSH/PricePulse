from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.models import Product, PriceHistory
from app.scraper import scrape_price
from app.sheets import sync_to_sheets

scheduler = BackgroundScheduler()

def scrape_all_products():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        for product in products:
            result = scrape_price(product.url)
            if not result["success"]:
                continue

            last = db.query(PriceHistory).filter(
                PriceHistory.product_id == product.id
            ).order_by(PriceHistory.scraped_at.desc()).first()

            change_detected = last is None or last.price != result["price"]

            entry = PriceHistory(
                product_id=product.id,
                price=result["price"],
                change_detected=change_detected
            )
            db.add(entry)
        db.commit()
        sync_to_sheets()
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(scrape_all_products, "interval", minutes=30)
    scheduler.start()