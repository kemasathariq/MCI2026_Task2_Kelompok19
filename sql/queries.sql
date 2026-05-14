-- Metabase Queries - MCI2026 Kelompok 19

-- 1. Total produk per department
SELECT
    department,
    COUNT(*) AS total_products
FROM mci_db.orders
GROUP BY department
ORDER BY total_products DESC;

-- 2. Distribusi order berdasarkan hari (day of week)
SELECT
    order_dow,
    COUNT(DISTINCT order_id) AS total_orders
FROM mci_db.orders
GROUP BY order_dow
ORDER BY order_dow;

-- 3. Distribusi order berdasarkan jam
SELECT
    order_hour_of_day,
    COUNT(DISTINCT order_id) AS total_orders
FROM mci_db.orders
GROUP BY order_hour_of_day
ORDER BY order_hour_of_day;

-- 4. Reorder rate per department
SELECT
    department,
    SUM(reordered) AS reordered_count,
    COUNT(*) AS total,
    ROUND(SUM(reordered) / COUNT(*) * 100, 2) AS reorder_rate_pct
FROM mci_db.orders
GROUP BY department
ORDER BY reorder_rate_pct DESC;

-- 5. Top 10 produk paling sering dipesan
SELECT
    product_name,
    COUNT(*) AS total_ordered
FROM mci_db.orders
GROUP BY product_name
ORDER BY total_ordered DESC
LIMIT 10;
