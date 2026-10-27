import json
import os
import random
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException, Query

random.seed(42)

SALES_FILE = "raw_sales.json"
EXPENSES_FILE = "raw_expenses.json"


# 1. Product catalogue
PRODUCTS = [
    {"product_id": "P001", "name": "Wireless Earbuds", "category": "Electronics", "cost_price": 2200, "sell_price": 3999},
    {"product_id": "P002", "name": "Power Bank", "category": "Electronics", "cost_price": 1100, "sell_price": 1899},
    {"product_id": "P003", "name": "Smart Watch", "category": "Electronics", "cost_price": 4500, "sell_price": 7499},
    {"product_id": "P004", "name": "Pashmina Shawl", "category": "Clothing", "cost_price": 1800, "sell_price": 3500},
    {"product_id": "P005", "name": "Trekking Jacket", "category": "Clothing", "cost_price": 3800, "sell_price": 6500},
    {"product_id": "P006", "name": "Ceramic Mug Set", "category": "Home", "cost_price": 700, "sell_price": 1400},
    {"product_id": "P007", "name": "Bedsheet Set", "category": "Home", "cost_price": 1500, "sell_price": 2800},
    {"product_id": "P008", "name": "Table Lamp", "category": "Home", "cost_price": 1300, "sell_price": 2600},
    {"product_id": "P009", "name": "Momo Pack", "category": "Food", "cost_price": 180, "sell_price": 350},
    {"product_id": "P010", "name": "Masala Tea", "category": "Food", "cost_price": 120, "sell_price": 250},
    {"product_id": "P011", "name": "Dried Fruits Box", "category": "Food", "cost_price": 600, "sell_price": 1100},
    {"product_id": "P012", "name": "Singing Bowl", "category": "Handicraft", "cost_price": 900, "sell_price": 2200},
    {"product_id": "P013", "name": "Thangka Painting", "category": "Handicraft", "cost_price": 3000, "sell_price": 6000},
]


# 2. Companies, regions, payments
COMPANIES = [
    "Himalayan Traders",
    "Everest Electronics",
    "Kathmandu Foods",
    "Pokhara Outfitters",
    "Annapurna Home",
]

REGIONS = ["Kathmandu", "Lalitpur", "Bhaktapur", "Pokhara", "Chitwan"]
PAYMENTS = ["Cash", "Card", "eSewa", "Khalti"]


# 3. Expense settings (monthly budget per company, split by type)
EXPENSE_BUDGET = {
    "Himalayan Traders": 450_000,
    "Everest Electronics": 500_000,
    "Kathmandu Foods": 800_000,
    "Pokhara Outfitters": 850_000,
    "Annapurna Home": 400_000,
}

EXPENSE_SPLIT = {
    "Rent": 0.30,
    "Salaries": 0.40,
    "Marketing": 0.15,
    "Utilities": 0.08,
    "Delivery": 0.07,
}


# 4. Mess makers
def messy_company(name):
    return random.choice([name, name, name.upper(), name.lower(), f"  {name} "])


def messy_date(d):
    formats = ["%Y-%m-%d", "%Y-%m-%d", "%d/%m/%Y", "%b %d %Y"]
    return d.strftime(random.choice(formats))


def messy_month(year, month):
    return random.choice([
        f"{year}-{month:02d}",
        f"{year}-{month:02d}",
        date(year, month, 1).strftime("%b %Y"),
        f"{month}/{year}",
    ])


def messy_money(amount):
    roll = random.random()
    if roll < 0.02:
        return None
    if roll < 0.15:
        return f"Rs {amount:,}"
    if roll < 0.30:
        return str(amount)
    return amount


def messy_int(value):
    roll = random.random()
    if roll < 0.10:
        return str(value)
    if roll < 0.18:
        return float(value)
    return value


def maybe_null(value, rate=0.03):
    return None if random.random() < rate else value


# 5. One order row
def make_order(order_id, day):
    product = random.choice(PRODUCTS)

    quantity = random.randint(1, 10)
    if random.random() < 0.02:
        quantity = random.choice([0, -1, -5])
    if random.random() < 0.005:
        quantity = 999

    discount_pct = random.choice([0, 0, 0, 5, 10, 15, 20])
    gross_sales = product["sell_price"] * quantity
    discount_amount = round(gross_sales * discount_pct / 100)
    revenue = gross_sales - discount_amount
    total_cost = product["cost_price"] * quantity
    profit = revenue - total_cost

    if random.random() < 0.02:
        profit = profit + random.randint(-5000, 5000)

    discount_value = discount_pct
    if random.random() < 0.05:
        discount_value = None
    elif random.random() < 0.10:
        discount_value = f"{discount_pct}%"

    return {
        "order_id": messy_int(order_id),
        "order_date": maybe_null(messy_date(day), 0.01),
        "company": maybe_null(messy_company(random.choice(COMPANIES)), 0.02),
        "product_id": product["product_id"],
        "product_name": maybe_null(product["name"]),
        "category": maybe_null(product["category"]),
        "quantity": messy_int(quantity),
        "cost_price": messy_money(product["cost_price"]),
        "sell_price": messy_money(product["sell_price"]),
        "discount_pct": discount_value,
        "discount_amount": maybe_null(discount_amount),
        "revenue": messy_money(revenue),
        "total_cost": messy_money(total_cost),
        "profit": maybe_null(profit, 0.02),
        "region": maybe_null(random.choice(REGIONS)),
        "payment_method": maybe_null(random.choice(PAYMENTS), 0.04),
        "customer_id": maybe_null(f"C{random.randint(1, 500):04d}", 0.05),
        "is_returned": random.choice(["yes", "no", "No", "N", "true", "0"]),
        "_internal_row_hash": f"{random.getrandbits(64):016x}",
        "legacy_sku": f"OLD-{random.randint(10000, 99999)}",
        "sync_status": random.choice(["SYNCED", "PENDING", "synced", None]),
        "ui_color": random.choice(["#FF5733", "#33C1FF", "#9B59B6"]),
        "deprecated_field": None,
        "batch_upload_ts": f"{random.randint(1700000000, 1790000000)}",
    }


# 6. All orders (about 1,400 rows including ~3% duplicates)
def generate_orders(days=90, avg_orders=15):
    start = date.today() - timedelta(days=days)
    orders = []
    order_id = 1

    for i in range(days):
        day = start + timedelta(days=i)
        for _ in range(random.randint(avg_orders - 5, avg_orders + 5)):
            orders.append(make_order(order_id, day))
            order_id += 1

    duplicates = random.sample(orders, k=len(orders) // 30)
    orders.extend(dict(order) for order in duplicates)
    random.shuffle(orders)
    return orders


# 7. Monthly expenses
def generate_expenses(days=90):
    start = date.today() - timedelta(days=days)
    months = []
    current = date(start.year, start.month, 1)
    while current <= date.today():
        months.append((current.year, current.month))
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)

    expenses = []
    expense_id = 1
    for company, budget in EXPENSE_BUDGET.items():
        for year, month in months:
            for expense_type, share in EXPENSE_SPLIT.items():
                amount = round(budget * share * random.uniform(0.85, 1.15))
                expenses.append({
                    "expense_id": messy_int(expense_id),
                    "company": maybe_null(messy_company(company), 0.02),
                    "month": messy_month(year, month),
                    "expense_type": maybe_null(expense_type),
                    "amount": messy_money(amount),
                    "approved_by": random.choice(["admin", "ADMIN", "system", None]),
                    "notes": random.choice(["", "n/a", "N/A", None, "check later"]),
                })
                expense_id += 1
    return expenses


# 8. Create the data files once, then load them
def load_or_create(path, generator):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(generator(), f, indent=2)
    with open(path) as f:
        return json.load(f)


ORDERS = load_or_create(SALES_FILE, generate_orders)
EXPENSES = load_or_create(EXPENSES_FILE, generate_expenses)


# 9. API
app = FastAPI(title="Company Financials API")


def paginate(items, page, page_size):
    start = (page - 1) * page_size
    return {
        "page": page,
        "page_size": page_size,
        "total_records": len(items),
        "total_pages": (len(items) + page_size - 1) // page_size,
        "data": items[start:start + page_size],
    }


@app.get("/orders")
def get_orders(page: int = Query(1, ge=1), page_size: int = Query(500, ge=1, le=1000)):
    return paginate(ORDERS, page, page_size)


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    matches = [order for order in ORDERS if str(order["order_id"]).split(".")[0] == str(order_id)]
    if not matches:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order_id, "records": matches}


@app.get("/expenses")
def get_expenses(page: int = Query(1, ge=1), page_size: int = Query(500, ge=1, le=1000)):
    return paginate(EXPENSES, page, page_size)


@app.get("/products")
def get_products():
    return {"total_records": len(PRODUCTS), "data": PRODUCTS}


@app.get("/companies")
def get_companies():
    return {"companies": COMPANIES}