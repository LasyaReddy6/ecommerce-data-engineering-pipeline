"""Generate deterministic sample data for local testing."""
from pathlib import Path
import pandas as pd
from src.config import PROJECT_ROOT

rows = [
    {"order_id":"1001","order_date":"2026-10-01","product_name":"Laptop","category":"Electronics","quantity":1,"unit_price":45000,"customer_id":"C001","customer_name":"Ananya Rao","city":"Bengaluru"},
    {"order_id":"1002","order_date":"2026-10-02","product_name":"Headphones","category":"Electronics","quantity":2,"unit_price":1500,"customer_id":"C002","customer_name":"Rahul Kumar","city":"Hyderabad"},
    {"order_id":"1003","order_date":"2026-10-03","product_name":"Chair","category":"Furniture","quantity":1,"unit_price":5000,"customer_id":"C003","customer_name":"Priya Reddy","city":"Chennai"},
    {"order_id":"1004","order_date":"2026-10-04","product_name":"Keyboard","category":"Electronics","quantity":3,"unit_price":800,"customer_id":"C001","customer_name":"Ananya Rao","city":"Bengaluru"},
    {"order_id":"1005","order_date":"2026-10-05","product_name":"Desk","category":"Furniture","quantity":2,"unit_price":7000,"customer_id":"C004","customer_name":"Arjun Singh","city":"Hyderabad"},
    {"order_id":"1006","order_date":"2026-10-08","product_name":"Mouse","category":"Electronics","quantity":2,"unit_price":650,"customer_id":"C005","customer_name":"Meera Shah","city":"Mumbai"},
    {"order_id":"1007","order_date":"2026-10-12","product_name":"Office Chair","category":"Furniture","quantity":1,"unit_price":6200,"customer_id":"C003","customer_name":"Priya Reddy","city":"Chennai"},
    {"order_id":"1008","order_date":"2026-10-15","product_name":"Monitor","category":"Electronics","quantity":2,"unit_price":12000,"customer_id":"C002","customer_name":"Rahul Kumar","city":"Hyderabad"},
    {"order_id":"1009","order_date":"2026-10-18","product_name":"Desk Lamp","category":"Home","quantity":4,"unit_price":900,"customer_id":"C006","customer_name":"Sana Ali","city":"Pune"},
    {"order_id":"1010","order_date":"2026-10-20","product_name":"Laptop Stand","category":"Accessories","quantity":2,"unit_price":1800,"customer_id":"C005","customer_name":"Meera Shah","city":"Mumbai"},
]
path = PROJECT_ROOT / "data" / "sample_orders.csv"
path.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(path, index=False)
print(f"Created {path} with {len(rows)} sample rows.")
