import re
from playwright.sync_api import sync_playwright

def scrape_price(url: str, price_selector: str = None) -> dict:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)

            title = page.title()

            if price_selector:
                element = page.query_selector(price_selector)
            else:
                element = page.query_selector("p.price_color")

            if not element:
                browser.close()
                return {"success": False, "error": "Price element not found. Check your selector."}

            raw_text = element.inner_text()
            numbers = re.findall(r"\d+[\.,]\d+", raw_text)

            browser.close()

            if not numbers:
                return {"success": False, "error": f"Could not extract number from: {raw_text}"}

            price_str = numbers[0].replace(",", ".")
            price = float(price_str)

            return {"success": True, "price": price, "name": title}

    except Exception as e:
        return {"success": False, "error": str(e)}