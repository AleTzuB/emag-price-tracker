import psycopg2
import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime

DATABASE_URL = os.getenv("POSTGRES_URL")  # Railway env var

PRODUCTS = [
    {"name": "Sapphire RX 7900XTX", "url": "https://www.emag.ro/placa-video-amd-sapphire-radeontm-rx-7900xtx-pulse-24gb-gddr6-384-bit-11322-02-20g/pd/D8KPF5MBM/"},
    {"name": "Gigabyte RTX 5070 Ti Eagle", "url": "https://www.emag.ro/placa-video-gigabyte-geforce-rtxtm-5070-ti-eagle-oc-sff-16gb-gddr7-256-bit-gv-n507teagle-oc-16gd/pd/D7GQ7B3BM/"},
    {"name": "Palit RTX 5070 Ti GamingPro", "url": "https://www.emag.ro/placa-video-palit-geforce-rtx-5070-ti-gamingpro-16gb-gddr7-256-bit-dlss-4-0-ne7507t019t2-gb2031a/pd/DGVT623BM/"},
    {"name": "Asus TUF RTX 5070 OC", "url": "https://www.emag.ro/placa-video-asus-tuf-gaming-geforce-rtxtm-5070-oc-edition-12gb-gddr7-192-bit-tuf-rtx5070-o12g-gaming/pd/DXLPN23BM/"},
    {"name": "Gigabyte RTX 5070 Ti Gaming OC", "url": "https://www.emag.ro/placa-video-gigabyte-geforce-rtxtm-5070-ti-gaming-oc-16gb-gddr7-256-bit-gv-n507tgaming-oc-16gd/pd/DG8Q7B3BM/"},
]

def get_price(product_url):
    response = requests.get(product_url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    price_element = soup.select_one(".product-new-price")
    if not price_element:
        return None
    price_text = price_element.get_text(strip=True)
    price = "".join([c for c in price_text if c.isdigit()])
    return float(price) / 100

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for product in PRODUCTS:
        cur.execute("INSERT INTO products (name, url) VALUES (%s, %s) ON CONFLICT DO NOTHING RETURNING id", (product["name"], product["url"]))
        product_id = cur.fetchone()[0] if cur.rowcount > 0 else None

        if not product_id:
            cur.execute("SELECT id FROM products WHERE url = %s", (product["url"],))
            product_id = cur.fetchone()[0]

        price = get_price(product["url"])
        if price:
            cur.execute("INSERT INTO price_history (product_id, price) VALUES (%s, %s)", (product_id, price))
            print(f"[{datetime.now()}] {product['name']}: {price} RON")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
