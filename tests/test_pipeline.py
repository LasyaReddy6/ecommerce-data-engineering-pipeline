import pandas as pd
import pytest
from src.pipeline import clean_data


def sample_frame():
    return pd.DataFrame([{
        "order_id": "1", "order_date": "2026-10-01", "product_name": "Laptop",
        "category": "Electronics", "quantity": 2, "unit_price": 10.50,
        "customer_id": "C1", "customer_name": "A Person", "city": "Anantapur"
    }])


def test_clean_data_calculates_revenue():
    cleaned = clean_data(sample_frame())
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["total_amount"] == 21.0
    assert cleaned.iloc[0]["quantity"] == 2


def test_clean_data_removes_invalid_quantity():
    frame = sample_frame()
    frame.loc[0, "quantity"] = 0
    with pytest.raises(ValueError, match="No valid rows remain"):
        clean_data(frame)


def test_clean_data_deduplicates_identical_lines():
    frame = pd.concat([sample_frame(), sample_frame()], ignore_index=True)
    cleaned = clean_data(frame)
    assert len(cleaned) == 1
