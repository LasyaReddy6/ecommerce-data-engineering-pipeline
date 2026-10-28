"""ETL pipeline: CSV -> validation/cleaning -> PostgreSQL star schema."""
from __future__ import annotations
import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from src.config import database_url, csv_path, PROJECT_ROOT

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger(__name__)
REQUIRED_COLUMNS = {
    "order_id", "order_date", "product_name", "category", "quantity",
    "unit_price", "customer_id", "customer_name", "city"
}


def load_source(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    df = pd.read_csv(path, dtype={"order_id": "string", "customer_id": "string"})
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate rows, normalize fields, and derive revenue and stable line IDs."""
    data = df.copy()
    for col in ["order_id", "product_name", "category", "customer_id", "customer_name", "city"]:
        data[col] = data[col].astype("string").str.strip()
    data["order_date"] = pd.to_datetime(data["order_date"], errors="coerce").dt.date
    data["quantity"] = pd.to_numeric(data["quantity"], errors="coerce")
    data["unit_price"] = pd.to_numeric(data["unit_price"], errors="coerce")

    text_cols = ["order_id", "product_name", "category", "customer_id", "customer_name", "city"]
    valid = data[text_cols].notna().all(axis=1)
    for col in text_cols:
        valid &= data[col].ne("")
    valid &= data["order_date"].notna()
    valid &= data["quantity"].notna() & (data["quantity"] > 0) & (data["quantity"] % 1 == 0)
    valid &= data["unit_price"].notna() & (data["unit_price"] >= 0)
    rejected = int((~valid).sum())
    if rejected:
        LOGGER.warning("Rejecting %s invalid row(s).", rejected)
    data = data.loc[valid].copy()
    if data.empty:
        raise ValueError("No valid rows remain after cleaning; check the source CSV.")

    data["quantity"] = data["quantity"].astype("int64")
    data["unit_price"] = data["unit_price"].round(2)
    data["total_amount"] = (data["quantity"] * data["unit_price"]).round(2)
    # Each CSV row is an order line. Duplicate identical source lines are removed.
    key_cols = ["order_id", "order_date", "product_name", "category", "customer_id", "quantity", "unit_price"]
    data = data.drop_duplicates(subset=key_cols, keep="first").copy()
    data["source_order_line_id"] = data[key_cols].astype(str).agg("|".join, axis=1)
    return data.reset_index(drop=True)


def execute_sql_file(engine: Engine, relative_path: str) -> None:
    sql = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
    # Each SQL file contains simple statements; execute them separately.
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))


def load_warehouse(df: pd.DataFrame, engine: Engine) -> dict[str, int]:
    """Upsert dimensions and idempotently insert fact rows."""
    execute_sql_file(engine, "sql/01_schema.sql")
    with engine.begin() as conn:
        # Date dimension
        dates = sorted(set(df["order_date"]))
        for dt in dates:
            date_key = int(dt.strftime("%Y%m%d"))
            conn.execute(text("""
                INSERT INTO dw.dim_date
                (date_key, full_date, day_of_month, month_number, month_name, quarter_number, year_number)
                VALUES (:date_key, :full_date, :day, :month, :month_name, :quarter, :year)
                ON CONFLICT (full_date) DO NOTHING
            """), {"date_key": date_key, "full_date": dt, "day": dt.day, "month": dt.month,
                  "month_name": dt.strftime("%B"), "quarter": (dt.month - 1)//3 + 1, "year": dt.year})

        products = df[["product_name", "category"]].drop_duplicates()
        for row in products.itertuples(index=False):
            conn.execute(text("""
                INSERT INTO dw.dim_product (product_name, category) VALUES (:name, :category)
                ON CONFLICT (product_name, category) DO NOTHING
            """), {"name": row.product_name, "category": row.category})

        customers = df[["customer_id", "customer_name", "city"]].drop_duplicates(subset=["customer_id"])
        # Customer ID is the stable business key; update descriptive attributes if changed.
        for row in customers.itertuples(index=False):
            conn.execute(text("""
                INSERT INTO dw.dim_customer (customer_id, customer_name, city)
                VALUES (:customer_id, :name, :city)
                ON CONFLICT (customer_id) DO UPDATE SET
                  customer_name = EXCLUDED.customer_name, city = EXCLUDED.city
            """), {"customer_id": row.customer_id, "name": row.customer_name, "city": row.city})

        inserted = 0
        for row in df.itertuples(index=False):
            result = conn.execute(text("""
                INSERT INTO dw.fact_sales
                (order_id, order_date, date_key, product_key, customer_key, quantity, unit_price, total_amount, source_order_line_id)
                SELECT :order_id, :order_date, :date_key, p.product_key, c.customer_key,
                       :quantity, :unit_price, :total_amount, :line_id
                FROM dw.dim_product p
                JOIN dw.dim_customer c ON c.customer_id = :customer_id
                WHERE p.product_name = :product_name AND p.category = :category
                ON CONFLICT (source_order_line_id) DO NOTHING
            """), {
                "order_id": row.order_id, "order_date": row.order_date,
                "date_key": int(row.order_date.strftime("%Y%m%d")),
                "product_name": row.product_name, "category": row.category,
                "customer_id": row.customer_id, "quantity": int(row.quantity),
                "unit_price": Decimal(str(row.unit_price)), "total_amount": Decimal(str(row.total_amount)),
                "line_id": row.source_order_line_id,
            })
            inserted += result.rowcount
    execute_sql_file(engine, "sql/02_analytics_views.sql")
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM dw.fact_sales")).scalar_one()
    return {"valid_rows": len(df), "new_fact_rows_inserted": inserted, "fact_rows_total": int(count)}


def run_pipeline() -> dict[str, int]:
    path = csv_path()
    LOGGER.info("Reading source CSV: %s", path)
    raw = load_source(path)
    cleaned = clean_data(raw)
    engine = create_engine(database_url(), pool_pre_ping=True)
    try:
        stats = load_warehouse(cleaned, engine)
        LOGGER.info("Pipeline completed: %s", stats)
        return stats
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_pipeline()
