# MCI2026 Task 2 - Kelompok 19

Pipeline Orchestration & Data Visualization menggunakan Apache Airflow, ClickHouse, dan Metabase.

## Anggota Kelompok
- Kemas Athariq
- Brilian

## Dataset
Source: `http://96.9.212.102:8000/orders`
- 100 orders, 1111 product rows (setelah flatten)
- 843 unique products, 105 aisles, 20 departments

## Struktur Repository
```
├── dags/
│   └── orders_pipeline.py    # Apache Airflow DAG
├── sql/
│   ├── ddl.sql               # DDL ClickHouse (CREATE TABLE)
│   └── queries.sql           # Query untuk Metabase
└── README.md
```

## Pipeline Overview

### 1. Apache Airflow DAG
DAG `orders_pipeline` terdiri dari 3 task:
- **extract**: Fetch data dari API endpoint
- **transform**: Flatten nested products, handle nulls
- **load**: Insert ke ClickHouse

### 2. ClickHouse
- Database: `mci_db`
- Tabel: `orders` (schema flat, 15 kolom)
- Engine: MergeTree, ORDER BY (order_id, product_id)

### 3. Metabase Dashboard
**Dashboard**
Dashboard Orders Dashboard - Kelompok 19 (Thariq & Brilian) menggabungkan seluruh 5 questions dalam satu tampilan:

- Baris atas: Order per Jam + Reorder Rate per Department

- Baris tengah: Produk per Department + Order per Hari

- Baris bawah: Top 10 Produk Terlaris (lebar penuh)

**Screenshot — Dashboard Lengkap**
<img width="1686" height="1498" alt="image" src="https://github.com/user-attachments/assets/cfc6d765-810e-4709-a405-8b859c753f72" />


---

## EDA Summary

| Metrik | Nilai |
|---|---|
| Total orders | 100 |
| Total rows (flattened) | 979 |
| Avg produk per order | 11.1 |
| Nulls di days_since_prior_order | 5 |
| Top department | produce (321 produk) |
| Peak jam order | 13:00–15:00 |
| Peak hari order | Minggu & Senin |
| Reordered rate | 63.9% |
