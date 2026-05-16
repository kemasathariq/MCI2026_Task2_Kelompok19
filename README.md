# MCI2026 Task 2 - Kelompok 19

Pipeline Orchestration & Data Visualization menggunakan Apache Airflow, ClickHouse, dan Metabase.

## Anggota Kelompok
- Kemas Athariq
- Brilian

## Dataset
Source: `http://96.9.212.102:8000/orders`
- 100 orders, 979 product rows (setelah flatten)
- 843 unique products, 105 aisles, 20 departments

## Struktur Repository
```
├── dags/
│   └── orders_pipeline.py    # Apache Airflow DAG
├── sql/
│   ├── ddl.sql               # DDL ClickHouse (CREATE TABLE)
│   └── queries.sql           # Query untuk Metabase
├── docs/
│   └── screenshots/          # Screenshot dokumentasi
├── Dockerfile                # Docker image untuk Airflow
├── docker-compose.yml        # Setup infrastruktur lengkap
└── README.md
```

---

## Arsitektur Pipeline

```
REST API  →  Apache Airflow  →  ClickHouse  →  Metabase
/orders      (ETL Pipeline)     (mci_db)       (Dashboard)
```

Data diambil dari REST API dalam format JSON nested (orders → products), di-flatten menjadi tabel flat di ClickHouse, lalu divisualisasikan di Metabase.

---

## 1. Setup Infrastruktur

Seluruh infrastruktur dijalankan menggunakan Docker Compose:

```bash
docker-compose up -d
```

Layanan yang berjalan:

| Layanan | URL | Keterangan |
|---|---|---|
| Airflow UI | http://localhost:8080 | Orchestrator pipeline |
| ClickHouse | http://localhost:8123 | OLAP database |
| Metabase | http://localhost:3000 | Visualisasi & dashboard |

---

## 2. Apache Airflow DAG

DAG `orders_pipeline` terdiri dari 3 task yang berjalan secara berurutan:

```
extract  →  transform  →  load
```

| Task | Fungsi |
|---|---|
| `extract` | Fetch data dari API endpoint `http://96.9.212.102:8000/orders` |
| `transform` | Flatten nested array `products[]` menjadi baris flat, handle null values |
| `load` | Insert data ke tabel `mci_db.orders` di ClickHouse |

### Cara Menjalankan DAG

1. Buka Airflow UI di `http://localhost:8080`
2. Login dengan username `admin`, password `admin`
3. Cari DAG `orders_pipeline`
4. Klik toggle ON → klik tombol ▶ Trigger DAG
5. Pantau di tab Graph hingga semua task berwarna hijau

### Screenshot — DAG Berhasil

*(tambahkan screenshot Graph View semua task hijau di sini)*

---

## 3. ClickHouse — Database & Schema

### Membuat Database dan Tabel

DDL dijalankan satu per satu via HTTP interface karena ClickHouse tidak mendukung multi-statement dalam satu request:

```bash
# Buat database
curl "http://admin:rahasia@localhost:8123/" \
  --data-binary "CREATE DATABASE IF NOT EXISTS mci_db"

# Buat tabel
curl "http://admin:rahasia@localhost:8123/" \
  --data-binary "CREATE TABLE IF NOT EXISTS mci_db.orders (
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
  ORDER BY (order_id, product_id)"
```

### Schema Tabel `mci_db.orders`

| Kolom | Tipe | Keterangan |
|---|---|---|
| order_id | Int32 | ID unik order |
| user_id | Int32 | ID pelanggan |
| order_number | UInt16 | Urutan order ke-N milik user |
| order_dow | UInt8 | Hari dalam seminggu (0=Minggu, 6=Sabtu) |
| order_hour_of_day | UInt8 | Jam order dibuat (0–23) |
| days_since_prior_order | Nullable(Float32) | Hari sejak order sebelumnya |
| eval_set | String | Subset data: prior/train/test |
| product_id | Int32 | ID produk |
| product_name | String | Nama produk |
| aisle_id | UInt16 | ID lorong di toko |
| aisle | String | Nama lorong |
| department_id | UInt8 | ID departemen |
| department | String | Nama departemen |
| add_to_cart_order | UInt8 | Urutan produk dimasukkan ke keranjang |
| reordered | UInt8 | 1 = pernah dipesan sebelumnya |

### Verifikasi Data

```bash
# Cek jumlah baris
curl "http://admin:rahasia@localhost:8123/?query=SELECT+count()+FROM+mci_db.orders"
# Output: 979

# Cek jumlah order unik
curl "http://admin:rahasia@localhost:8123/?query=SELECT+uniqExact(order_id)+FROM+mci_db.orders"
# Output: 100
```

### Screenshot — Data Berhasil Masuk

*(tambahkan screenshot hasil query count() di sini)*

---

## 4. Metabase — Visualisasi & Dashboard

### Koneksi ke ClickHouse

1. Buka Metabase → Settings → Databases → Add Database
2. Pilih **ClickHouse**
3. Isi konfigurasi:

| Field | Value |
|---|---|
| Display name | ClickHouse MCI Task |
| Host | clickhouse-server |
| Port | 8123 |
| Database | mci_db |
| Username | admin |
| Password | rahasia |

### Screenshot — Koneksi Berhasil

*(tambahkan screenshot koneksi berhasil di sini)*

---

### Questions yang Dibuat

#### Q1 — Produk per Department
Menampilkan jumlah produk yang dipesan per departemen, diurutkan dari terbanyak.

```sql
SELECT department, count() AS total_produk
FROM mci_db.orders
GROUP BY department
ORDER BY total_produk DESC
```

**Visualisasi:** Bar chart | **Insight:** Departemen `produce` mendominasi dengan 290+ produk

*(tambahkan screenshot Q1 di sini)*

---

#### Q2 — Order per Hari (Day of Week)
Menampilkan pola pembelian berdasarkan hari dalam seminggu (0=Minggu, 6=Sabtu).

```sql
SELECT order_dow, count() AS total_orders
FROM mci_db.orders
GROUP BY order_dow
ORDER BY order_dow ASC
```

**Visualisasi:** Bar chart | **Insight:** Hari 0 (Minggu) dan hari 3 (Rabu) memiliki order terbanyak

*(tambahkan screenshot Q2 di sini)*

---

#### Q3 — Order per Jam
Menampilkan pola pembelian berdasarkan jam dalam sehari.

```sql
SELECT order_hour_of_day, count() AS total_orders
FROM mci_db.orders
GROUP BY order_hour_of_day
ORDER BY order_hour_of_day ASC
```

**Visualisasi:** Line chart | **Insight:** Peak order terjadi pada jam 10:00–15:00

*(tambahkan screenshot Q3 di sini)*

---

#### Q4 — Reorder Rate per Department
Menampilkan persentase produk yang merupakan reorder (dibeli ulang) per departemen.

```sql
SELECT department, round(avg(reordered) * 100, 2) AS reorder_rate_pct
FROM mci_db.orders
GROUP BY department
ORDER BY reorder_rate_pct DESC
```

**Visualisasi:** Bar chart | **Insight:** Departemen `pets` dan `alcohol` memiliki reorder rate tertinggi (~100%)

*(tambahkan screenshot Q4 di sini)*

---

#### Q5 — Top 10 Produk Terlaris
Menampilkan 10 produk yang paling sering muncul dalam order.

```sql
SELECT product_name, count() AS total_ordered
FROM mci_db.orders
GROUP BY product_name
ORDER BY total_ordered DESC
LIMIT 10
```

**Visualisasi:** Bar chart | **Insight:** Banana menjadi produk paling sering dipesan (11x), diikuti Bag of Organic Bananas (10x)

*(tambahkan screenshot Q5 di sini)*

---

### Dashboard

Dashboard `Orders Dashboard - Kelompok 19 (Thariq & Brilian)` menggabungkan seluruh 5 questions dalam satu tampilan:

- Baris atas: Order per Jam + Reorder Rate per Department
- Baris tengah: Produk per Department + Order per Hari
- Baris bawah: Top 10 Produk Terlaris (lebar penuh)

### Screenshot — Dashboard Lengkap

*(tambahkan screenshot dashboard di sini)*

---

## EDA Summary

| Metrik | Nilai |
|---|---|
| Total orders | 100 |
| Total rows (flattened) | 979 |
| Avg produk per order | 9.79 |
| Nulls di days_since_prior_order | 5 |
| Top department | produce (290+ produk) |
| Peak jam order | 10:00–15:00 |
| Peak hari order | Minggu (hari 0) |
| Reorder rate tertinggi | pets & alcohol (~100%) |
| Produk terlaris | Banana (11x) |
