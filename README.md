# PricePulse

A backend API that automatically tracks product prices from any website and delivers real-time alerts via Telegram and Google Sheets sync.

Built for e-commerce businesses, procurement teams, and anyone who needs to monitor prices without doing it manually.

---

## What It Does

- Tracks prices from any website including JavaScript-heavy sites
- Detects price changes automatically and sends Telegram alerts instantly
- Syncs all tracked products and price history to Google Sheets
- Runs on a schedule — no manual work required
- Full REST API with Swagger documentation

---

## Screenshots

### API Endpoints (Swagger UI)
![Swagger UI](swagger.png)

### Google Sheets Output
![Google Sheets](google_sheets.png)

### Telegram Price Alert
![Telegram Alert](telegram_alert.png)

---

## Tech Stack

- **Python 3.13**
- **FastAPI** — REST API framework
- **PostgreSQL + SQLAlchemy** — price history storage
- **Playwright** — headless browser scraping (handles any site)
- **APScheduler** — automated scheduling
- **Google Sheets API + gspread** — real-time reporting
- **Telegram Bot API** — instant price alerts
- **Docker** — containerized deployment

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DAAVISSH/pricepulse.git
cd pricepulse
```

### 2. Set up environment variables

Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/pricetracker
SPREADSHEET_ID=your_google_spreadsheet_id
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 3. Add Google credentials

Place your `credentials.json` file (Google Service Account) in the root directory.

### 4. Install dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 5. Create the database
```bash
psql -U postgres
CREATE DATABASE pricetracker;
\q
```

### 6. Run the API
```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for the full Swagger UI.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /products/ | Add a product to track |
| GET | /products/ | List all tracked products |
| DELETE | /products/{id} | Remove a product |
| GET | /products/{id}/history | Get full price history |
| GET | /products/{id}/price-change | Get latest price change details |
| POST | /products/scrape/{id} | Manually scrape a single product |
| POST | /products/scrape/all | Scrape all tracked products at once |
| POST | /products/sync/sheets | Sync all prices to Google Sheets |

---

## Adding a Product
```json
POST /products/
{
  "url": "https://www.alternate.de/ZOTAC/GeForce-RTX-5050-Twin-Edge-8GB-Grafikkarte/html/product/100141724",
  "name": "ZOTAC RTX 5050 Twin Edge 8GB",
  "price_selector": "span.price"
}
```

Response:
```json
{
  "id": 1,
  "name": "ZOTAC RTX 5050 Twin Edge 8GB",
  "url": "https://www.alternate.de/...",
  "price_selector": "span.price",
  "created_at": "2026-02-27T12:00:00"
}
```

---

## Telegram Alerts

When a price change is detected the system sends an instant Telegram message:
```
📉 Price Drop

🖥 ZOTAC RTX 5050 Twin Edge 8GB
Previous: €350.0
Current: €315.0
Change: €-35.0 (-10.0%)
```

---

## Google Sheets Output

The system syncs to a connected Google Sheet showing:

|     Product    |       URL        | Previous Price | Latest Price | Change | Last Scraped |
|----------------|------------------|----------------|--------------|--------|--------------|
| ZOTAC RTX 5050 | alternate.de/... |     €350.0     |    €315.0    | €-35.0 |  2026-02-27  |

---

## How to Find the Price Selector

1. Open the product page in your browser
2. Right click on the price -> Inspect
3. Find the HTML element containing the price
4. Copy its CSS selector — for example `span.price` or `div.product-price`
5. Pass it as `price_selector` when adding the product

---

## Docker
```bash
docker build -t pricepulse .
docker run -p 8000:8000 --env-file .env pricepulse
```

---

## Project Structure
```
pricepulse/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── scraper.py
│   ├── scheduler.py
│   ├── sheets.py
│   ├── telegram.py
│   └── routes/
│       └── products.py
├── .env
├── requirements.txt
├── Dockerfile
└── README.md

```

