-- DDL ClickHouse - MCI2026 Kelompok 19
-- Buat database
CREATE DATABASE IF NOT EXISTS mci_db;

-- Buat tabel orders (flat schema, 1 row = 1 produk per order)
CREATE TABLE IF NOT EXISTS mci_db.orders (
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
ORDER BY (order_id, product_id);
