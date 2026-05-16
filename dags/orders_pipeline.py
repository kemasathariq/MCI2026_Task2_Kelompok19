from airflow.decorators import dag, task
from datetime import datetime
import requests
from clickhouse_driver import Client

API_URL = "http://96.9.212.102:8000/orders"

CLICKHOUSE_HOST = "clickhouse-server"
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = "admin"
CLICKHOUSE_PASSWORD = "rahasia"
CLICKHOUSE_DB   = "mci_db"
CLICKHOUSE_TABLE = "orders"


@dag(
    dag_id="orders_pipeline",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mci", "kelompok19"],
)
def orders_pipeline():

    @task()
    def extract() -> list:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        print(f"Fetched {data['total_orders']} orders from API")
        return data["orders"]

    @task()
    def transform(orders: list) -> list:
        rows = []
        for order in orders:
            base = {
                "order_id":               order["order_id"],
                "user_id":                order["user_id"],
                "order_number":           order["order_number"],
                "order_dow":              order["order_dow"],
                "order_hour_of_day":      order["order_hour_of_day"],
                "days_since_prior_order": order["days_since_prior_order"],
                "eval_set":               order["eval_set"],
            }
            for product in order["products"]:
                rows.append({
                    **base,
                    "product_id":       product["product_id"],
                    "product_name":     product["product_name"],
                    "aisle_id":         product["aisle_id"],
                    "aisle":            product["aisle"],
                    "department_id":    product["department_id"],
                    "department":       product["department"],
                    "add_to_cart_order": product["add_to_cart_order"],
                    "reordered":        product["reordered"],
                })
        print(f"Transformed {len(orders)} orders → {len(rows)} rows (flattened)")
        return rows

    @task()
    def load(rows: list) -> None:
        client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, user=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD)

        client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB}")

        client.execute(f"""
            CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB}.{CLICKHOUSE_TABLE} (
                order_id               Int32,
                user_id                Int32,
                order_number           UInt16,
                order_dow              UInt8,
                order_hour_of_day      UInt8,
                days_since_prior_order Nullable(Float32),
                eval_set               String,
                product_id             Int32,
                product_name           String,
                aisle_id               UInt16,
                aisle                  String,
                department_id          UInt8,
                department             String,
                add_to_cart_order      UInt8,
                reordered              UInt8
            ) ENGINE = MergeTree()
            ORDER BY (order_id, product_id)
        """)

        client.execute(
            f"INSERT INTO {CLICKHOUSE_DB}.{CLICKHOUSE_TABLE} VALUES",
            rows,
        )
        print(f"Loaded {len(rows)} rows into {CLICKHOUSE_DB}.{CLICKHOUSE_TABLE}")

    raw     = extract()
    cleaned = transform(raw)
    load(cleaned)


orders_pipeline()
