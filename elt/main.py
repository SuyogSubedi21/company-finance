from extract import extract
from load import load


def run():
    pages = extract("orders")
    load("orders", "orders_raw", pages)

    pages = extract("expenses")
    load("expenses", "expenses_raw", pages)

if __name__ == "__main__":
    run()