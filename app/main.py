from fastapi import FastAPI
from app.database import engine, Base
from app.routes import products
from app.scheduler import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Price Tracker")

app.include_router(products.router, prefix="/products", tags=["Products"])

@app.on_event("startup")
def startup_event():
    start_scheduler()

@app.get("/")
def root():
    return {"message": "Price Tracker API is running"}