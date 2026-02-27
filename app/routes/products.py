from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, PriceHistory
from app.scraper import scrape_price
from app.sheets import sync_to_sheets
from pydantic import BaseModel
from app.telegram import send_price_alert

router = APIRouter()

class ProductCreate(BaseModel):
    url: str
    name: str | None = None
    price_selector: str | None = None

@router.post("/")
def add_product(product: ProductCreate, db: Session = Depends(get_db)):
    existing = db.query(Product).filter(Product.url == product.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already exists")
    new_product = Product(url=product.url, name=product.name, price_selector=product.price_selector)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.query(PriceHistory).filter(PriceHistory.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}

@router.get("/{product_id}/history")
def get_history(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product.history

@router.post("/scrape/{product_id}")
def scrape_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = scrape_price(product.url, product.price_selector)

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    last = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).order_by(PriceHistory.scraped_at.desc()).first()

    change_detected = last is not None and last.price != result["price"]

    if not product.name:
        product.name = result["name"]
        db.commit()

    entry = PriceHistory(
        product_id=product_id,
        price=result["price"],
        change_detected=change_detected
    )
    db.add(entry)
    db.commit()

    if change_detected and last:
        send_price_alert(product.name, last.price, result["price"])

    return {
        "product": product.name,
        "price": result["price"],
        "change_detected": change_detected
    }

@router.post("/sync/sheets")
def sync_sheets():
    try:
        sync_to_sheets()
        return {"message": "Synced to Google Sheets successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/{product_id}/price-change")
def get_price_change(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    history = db.query(PriceHistory).filter(
        PriceHistory.product_id == product_id
    ).order_by(PriceHistory.scraped_at.desc()).limit(2).all()

    if len(history) < 2:
        return {
            "product": product.name,
            "current_price": history[0].price if history else None,
            "previous_price": None,
            "change": None,
            "change_percent": None,
            "message": "Not enough history yet"
        }

    current = history[0].price
    previous = history[1].price
    change = round(current - previous, 2)
    change_percent = round((change / previous) * 100, 2)

    return {
        "product": product.name,
        "current_price": current,
        "previous_price": previous,
        "change": change,
        "change_percent": f"{change_percent}%"
    }

@router.post("/scrape/all")
def scrape_all(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    results = []
    for product in products:
        result = scrape_price(product.url, product.price_selector)

        if not result["success"]:
            results.append({"product": product.name, "error": result["error"]})
            continue

        last = db.query(PriceHistory).filter(
            PriceHistory.product_id == product.id
        ).order_by(PriceHistory.scraped_at.desc()).first()

        change_detected = last is not None and last.price != result["price"]

        entry = PriceHistory(
            product_id=product.id,
            price=result["price"],
            change_detected=change_detected
        )
        db.add(entry)
        if change_detected and last:
            send_price_alert(product.name, last.price, result["price"])

        results.append({
            "product": product.name,
            "price": result["price"],
            "change_detected": change_detected
        })

    db.commit()
    return results