# Power BI setup

1. Run the pipeline successfully at least once.
2. In Power BI Desktop, choose **Get Data → PostgreSQL database**.
3. Server: `localhost:5432`; database: `ecommerce_dw` (or your `.env` values).
4. Use the configured database credentials. For this local Docker setup, the user is `ecommerce_user` and the password is the value in `.env`.
5. Select these views from schema `dw`: `vw_sales_kpis`, `vw_monthly_revenue`, `vw_product_performance`, `vw_city_revenue`. You can also load dimensions/fact tables for date and category slicers.
6. Suggested visuals:
   - Cards: `total_revenue`, `total_orders`, `units_sold`, `average_order_value`.
   - Line chart: year/month vs revenue.
   - Bar chart: product_name vs revenue or units_sold.
   - Bar chart: city vs revenue.
   - Slicers: year, month, category, city.

## Refresh notes

Power BI Desktop can refresh from the local database when the pipeline has run. Automated scheduled refresh depends on where Power BI is hosted and the network/gateway setup. A local PostgreSQL database is not automatically accessible to the Power BI cloud service; configure a supported gateway or host the database in a reachable environment if you publish and require cloud refresh.
