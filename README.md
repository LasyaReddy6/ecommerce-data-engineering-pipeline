# End-to-End E-commerce Data Engineering Pipeline

A local portfolio project demonstrating CSV ingestion, data quality validation, Python ETL, a PostgreSQL star schema, analytics views, tests, and Power BI reporting. Apache Airflow support is included as an optional extension.

## Requirements

- Python 3.10 or newer
- Docker Desktop (recommended for PostgreSQL) OR a local PostgreSQL installation
- Power BI Desktop for the dashboard (Windows)

## Quick start (Docker PostgreSQL)

1. Open a terminal in this project folder.
2. Create your environment file:
   - Windows PowerShell: `Copy-Item .env.example .env`
   - macOS/Linux: `cp .env.example .env`
3. Edit `.env` and choose a local database password. The default is for local learning only; do not use it for a public server.
4. Create and activate a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
5. Install dependencies: `python -m pip install -r requirements.txt`
6. Start PostgreSQL: `docker compose up -d`
7. Generate sample data (optional; `data/sample_orders.csv` is already included): `python -m src.generate_sample_data`
8. Run the ETL: `python -m src.pipeline`
9. Run tests: `python -m pytest -q`
10. Follow `dashboard/POWER_BI_GUIDE.md` to connect Power BI.

The ETL creates schema `dw`, dimension/fact tables, and reporting views. Re-running the same CSV is idempotent for fact rows: existing source line IDs are not inserted twice. It updates customer descriptive fields when a known customer ID is encountered.

## CSV contract

The input CSV must contain: `order_id, order_date, product_name, category, quantity, unit_price, customer_id, customer_name, city`. Dates should be parseable by Pandas. Quantity must be a positive whole number; unit price must be non-negative. Invalid rows are logged and rejected. The project treats each source row as one order line; in this sample each order has one line.

## Run with a local PostgreSQL server instead

Create a database and user matching `.env`, or edit the variables to match your existing database. Make sure the database is running and reachable at `DB_HOST:DB_PORT`. Then run `python -m src.pipeline`.

## Scheduling

For a first version, schedule `python -m src.pipeline` with Windows Task Scheduler or cron after confirming it runs manually. An optional Airflow DAG is in `airflow/dags/ecommerce_sales_dag.py`. Airflow is not included in the standard requirements because it should be installed separately according to the official version-specific installation instructions. The DAG's project path and Python environment must be configured for your Airflow worker.

## Reporting views

- `dw.vw_sales_kpis`
- `dw.vw_monthly_revenue`
- `dw.vw_product_performance`
- `dw.vw_city_revenue`

## Project limitations / next steps

- Sample data is synthetic and only intended for learning.
- For production, add a proper source-system order-line ID, incremental extraction/watermarks, a rejected-record table, structured logs, stronger tests, secrets management, and monitoring.
- If an order can contain multiple lines, use a real order-line identifier from the source rather than relying on the generated composite key.
- Power BI refresh scheduling depends on deployment and gateway configuration.
