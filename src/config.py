"""Configuration helpers for the ecommerce pipeline."""
from pathlib import Path
import os
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def database_url() -> str:
    """Build a SQLAlchemy PostgreSQL URL from environment variables."""
    from sqlalchemy.engine import URL
    return URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("DB_USER", "ecommerce_user"),
        password=os.getenv("DB_PASSWORD", "change_me_locally"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "ecommerce_dw"),
    ).render_as_string(hide_password=False)


def csv_path() -> Path:
    value = Path(os.getenv("CSV_PATH", "data/sample_orders.csv"))
    return value if value.is_absolute() else PROJECT_ROOT / value
