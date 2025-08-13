import os, json, requests, re
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DB_URL = os.environ["POSTGRES_URL"]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7"
}

PRODUCTS = [
    "https://www.emag.ro/placa-video-amd-sapphire-radeontm-rx-7900xtx-pulse-24gb-gddr6-384-bit-11322-02-20g/pd/D8KPF5MBM/",
    "https://www.emag.ro/placa-video-gigabyte-geforce-rtxtm-5070-ti-eagle-oc-sff-16gb-gddr7-256-bit-gv-n507teagle-oc-16gd/pd/D7GQ7B3BM/",
    "https://www.emag.ro/placa-video-palit-geforce-rtx-5070-ti-gamingpro-16gb-gddr7-256-bit-dlss-4-0-ne7507t019t2-gb2031a/pd/DGVT623BM/",
    "https://www.emag.ro/placa-video-asus-tuf-gaming-geforce-rtxtm-5070-oc-edition-12gb-gddr7-192-bit-tuf-rtx5070-o12g-gaming/pd/DXLPN23BM/",
    "https://www.emag.ro/placa-video-gigabyte-geforce-rtxtm-5070-ti-gaming-oc-16gb-gddr7-256-bit-gv-n507tgaming-oc-16gd/pd/DG8Q7B3BM/"
]

def parse_price(text):
    t = text.replace("\xa0", " ")
    m = re.search(r"(\d[\d\. ]+)", t)
    if not m: return None
    return int(m.group(1).replace(".", "").replace(" ", "")) * 100

def scrape_emag(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "lxml")
    name = soup.find("title").get_text(strip=True).replace("- eMAG.ro", "").strip()
    price_tag = soup.select_one(".product-new-price, meta[itemprop=price]")
    if price_tag:
        if price_tag.name == "meta":
            price_cents = parse_price(price_tag["content"])
        else:
            price_cents = parse_price(price_tag.get_text())
    else:
        price_cents = None
    return name, price_cents, "RON"

def handler(request):
    conn = psycopg2.connect(DB_URL, sslmode="require", cursor_factory=RealDictCursor)
    cur = conn.cursor()

    results = []
    for url in PRODUCTS:
        name, price_cents, currency = scrape_emag(url)
        cur.execute("""
            INSERT INTO products (url, name, currency)
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO UPDATE SET name=EXCLUDED.name, currency=EXCLUDED.currency
            RETURNING id;
        """, (url, name, currency))
        pid = cur.fetchone()["id"]
        if price_cents:
            cur.execute("""
                INSERT INTO prices (product_id, price_cents, currency)
                VALUES (%s, %s, %s);
            """, (pid, price_cents, currency))
        results.append({"id": pid, "url": url, "name": name, "price": price_cents / 100 if price_cents else None, "currency": currency})

    conn.commit()
    cur.close()
    conn.close()
    return (json.dumps(results), 200, {"Content-Type": "application/json"})
