import os
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

SCHEMA = """
Table workspace.gold.company_daily_sales (one row per company per day)
  order_date, company, orders, units_sold, revenue, profit, revenue_7d_avg, revenue_month_to_date

Table workspace.gold.product_performance (one row per product)
  product_id, product_name, category, units_sold, revenue, profit,
  profit_margin_pct, avg_discount_pct, return_rate_pct, profit_rank_in_category

Table workspace.gold.company_monthly_pnl (one row per company per month)
  month, company, revenue, cost_of_goods, gross_profit, operating_expenses,
  net_profit, net_margin_pct, result ('Profit' or 'Loss')

Companies: Himalayan Traders, Everest Electronics, Kathmandu Foods, Pokhara Outfitters, Annapurna Home
Categories: Electronics, Clothing, Home, Food, Handicraft
Money is in Nepali rupees (Rs). Months are stored as the first day of the month, for example 2026-09-01.
"""


connection = None


def get_connection():
    global connection
    if connection is None:
        connection = sql.connect(
            server_hostname=os.getenv("DATABRICKS_HOST"),
            http_path=os.getenv("DATABRICKS_HTTP_PATH"),
            access_token=os.getenv("DATABRICKS_TOKEN"),
        )
    return connection


def run_query(query):
    global connection
    try:
        with get_connection().cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
        return columns, rows
    except Exception:
        connection = None
        raise