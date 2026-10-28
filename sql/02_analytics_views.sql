CREATE OR REPLACE VIEW dw.vw_sales_kpis AS
SELECT
    COALESCE(SUM(total_amount), 0)::NUMERIC(14,2) AS total_revenue,
    COUNT(DISTINCT order_id)::BIGINT AS total_orders,
    COALESCE(SUM(quantity), 0)::BIGINT AS units_sold,
    CASE WHEN COUNT(DISTINCT order_id) = 0 THEN 0
         ELSE (SUM(total_amount) / COUNT(DISTINCT order_id))::NUMERIC(14,2)
    END AS average_order_value
FROM dw.fact_sales;

CREATE OR REPLACE VIEW dw.vw_monthly_revenue AS
SELECT d.year_number, d.month_number, d.month_name,
       SUM(f.total_amount)::NUMERIC(14,2) AS revenue,
       COUNT(DISTINCT f.order_id)::BIGINT AS total_orders
FROM dw.fact_sales f
JOIN dw.dim_date d ON d.date_key = f.date_key
GROUP BY d.year_number, d.month_number, d.month_name;

CREATE OR REPLACE VIEW dw.vw_product_performance AS
SELECT p.product_name, p.category,
       SUM(f.quantity)::BIGINT AS units_sold,
       SUM(f.total_amount)::NUMERIC(14,2) AS revenue,
       COUNT(DISTINCT f.order_id)::BIGINT AS total_orders
FROM dw.fact_sales f
JOIN dw.dim_product p ON p.product_key = f.product_key
GROUP BY p.product_name, p.category;

CREATE OR REPLACE VIEW dw.vw_city_revenue AS
SELECT c.city,
       SUM(f.total_amount)::NUMERIC(14,2) AS revenue,
       COUNT(DISTINCT f.order_id)::BIGINT AS total_orders
FROM dw.fact_sales f
JOIN dw.dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.city;
