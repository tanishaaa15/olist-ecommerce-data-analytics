# Olist Interview API

## Overview

This project contains a REST API built using FastAPI and the Olist E-commerce dataset.

The purpose of this repository is to be used as a technical assessment for Data Analyst candidates.

The project includes SQLite database design, REST API development, SQL-based business analytics, authentication, pagination, input validation, and analytical endpoints for e-commerce performance analysis.

---

## Project Structure

```text
olist-interview-api/
│
├── api/
│   └── main.py
│
├── data/
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
│
├── scripts/
│   └── load_data.py
│
├── sql/
│   └── analytics_queries.sql
│
├── olist.db
├── requirements.txt
├── CANDIDATE_TASK.md
├── SUBMISSION_GUIDELINES.md
├── Olist E-commerce Sales & Performance Analytics Dashboard.png
├── README.md
└── Olist E-Commerce Sales & Analytics Dashboard.pbix
```

---

## Dataset

The CSV datasets are available inside the `data/` folder.

The project uses the following Olist datasets:

* Customers
* Orders
* Order Items
* Payments
* Reviews
* Products
* Sellers
* Geolocation
* Product Category Translation

### Dataset Availability

The original Olist CSV dataset is not included in this GitHub repository due to GitHub's individual file upload limitations. The dataset was used locally for database creation, API development, SQL analytics, and dashboard development.

To reproduce the project locally, place the Olist CSV files in the `data/` directory and run:

```bash
python scripts/load_data.py


---

## Database Design

The CSV datasets are loaded into SQLite with meaningful table names, appropriate data types, primary keys, and foreign key relationships.

### Tables and Keys

| Table                | Primary Key                    | Foreign Keys                                                                                |
| -------------------- | ------------------------------ | ------------------------------------------------------------------------------------------- |
| customers            | customer_id                    | —                                                                                           |
| orders               | order_id                       | customer_id → customers.customer_id                                                         |
| products             | product_id                     | —                                                                                           |
| sellers              | seller_id                      | —                                                                                           |
| category_translation | product_category_name          | —                                                                                           |
| order_items          | (order_id, order_item_id)      | order_id → orders.order_id; product_id → products.product_id; seller_id → sellers.seller_id |
| payments             | (order_id, payment_sequential) | order_id → orders.order_id                                                                  |
| reviews              | (review_id, order_id)          | order_id → orders.order_id                                                                  |
| geolocation          | geolocation_id                 | —                                                                                           |

Foreign key enforcement is enabled for database connections to maintain referential integrity.

The `products` table contains some product categories that do not have corresponding entries in `category_translation`, so a foreign key relationship was not enforced between these two tables.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/sambhatnagar4/olist-interview-api.git
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Load Database

Run:

```bash
python scripts/load_data.py
```

This will create the SQLite database (`olist.db`) from the CSV files.

The database loader creates the required tables, primary keys, foreign keys, and appropriate data types before loading the data.

---

## Start the API

Run:

```bash
uvicorn api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

After starting the server, open:

```text
http://127.0.0.1:8000/docs
```

FastAPI Swagger UI provides interactive documentation and allows the API endpoints to be tested directly.

Alternative documentation is available at:

```text
http://127.0.0.1:8000/redoc
```

---

## Authentication

All endpoints require the following API key:

```text
candidate-test-2026
```

Pass it in the request header:

```text
x-api-key: candidate-test-2026
```

Requests with a missing or invalid API key return:

```text
401 Unauthorized
```

---

## Pagination

Paginated endpoints support the following query parameters:

```text
page
limit
```

Example:

```text
GET /products?page=1&limit=100
```

Validation rules:

* `page` must be greater than or equal to 1.
* `limit` must be between 1 and 1000.

Paginated responses include:

* `page`
* `limit`
* `total_records`
* `returned_records`
* `has_next`
* `data`

---

## Available REST API Endpoints

### General

* GET `/`

### Customers

* GET `/customers`
* GET `/customers/{customer_id}`

### Orders

* GET `/orders`
* GET `/orders/{order_id}`
* GET `/orders/{order_id}/details`

### Products

* GET `/products`
* GET `/products/{product_id}`

### Categories

* GET `/categories`
* GET `/categories/translation`
* GET `/category_translation`

### Order Data

* GET `/order_items`
* GET `/payments`
* GET `/reviews`

### Sellers and Geolocation

* GET `/sellers`
* GET `/geolocation`

---

## Analytics API Endpoints

The analytical endpoints perform aggregations directly in SQL to avoid loading complete tables into pandas unnecessarily.

### Product Analytics

* GET `/analytics/top-selling-products`
* GET `/analytics/top-revenue-products`

### Revenue Analytics

* GET `/analytics/monthly-revenue`
* GET `/analytics/revenue-by-state`
* GET `/analytics/revenue-by-category`

### Customer and Order Analytics

* GET `/analytics/average-order-value`
* GET `/analytics/top-customers-lifetime-value`
* GET `/analytics/repeat-customers`
* GET `/analytics/average-basket-size`

### Delivery Analytics

* GET `/analytics/average-delivery-time`
* GET `/analytics/late-deliveries`

### Payment and Order Status Analytics

* GET `/analytics/payment-method-distribution`
* GET `/analytics/cancellation-rate`

### Growth Analytics

* GET `/analytics/monthly-order-growth`
* GET `/analytics/yoy-growth`

---

## Analytics Definitions and Assumptions

### Revenue

Revenue is calculated using the `price` field from `order_items`.

`freight_value` is excluded from revenue calculations.

Orders with the statuses `canceled` and `unavailable` are excluded from sales and revenue metrics.

### Average Order Value

Average Order Value (AOV) is calculated as:

```text
Total item-price revenue / Number of valid orders
```

Each order is counted once.

Canceled and unavailable orders are excluded.

### Revenue by State

Revenue is grouped using the customer's state from the `customers` table.

### Revenue by Category

Revenue is grouped using the product category from the `products` table.

### Lifetime Value

Customer lifetime value is calculated as the total item-price revenue associated with a customer's `customer_unique_id`.

Canceled and unavailable orders are excluded.

### Repeat Customers

A customer is considered a repeat customer when the same `customer_unique_id` has more than one order.

### Average Basket Size

Average basket size represents the average number of order items per valid order.

### Late Deliveries

A delivery is considered late when the actual customer delivery date is later than the estimated delivery date.

### Cancellation Rate

Cancellation rate is calculated as:

```text
Canceled orders / Total orders × 100
```

### Monthly Order Growth

Monthly order growth compares the number of valid orders with the previous available month.

### Year-over-Year Growth

YoY growth compares the number of valid orders for a month with the corresponding month from the previous year.

---

## Data Quality and Validation

The database was validated for:

* Primary key uniqueness
* Missing primary key values
* Foreign key integrity
* Table row counts
* Appropriate data types
* Pagination behavior
* API authentication
* Invalid API input
* Non-existent resource handling

Foreign key integrity checks confirmed that the implemented relationships contain no missing referenced records.

---

## Error Handling and Input Validation

The API includes:

* API key authentication
* `404 Not Found` responses for non-existent customers, products, and orders
* `401 Unauthorized` responses for missing or invalid API keys
* Query parameter validation for pagination
* `422 Unprocessable Entity` responses for invalid pagination parameters
* SQL-based aggregation for analytical queries

---

## API Testing

The implemented endpoints were tested using FastAPI Swagger UI.

Testing included:

* Successful requests with a valid API key
* Missing API key
* Invalid API key
* Existing product, customer, and order IDs
* Non-existent product, customer, and order IDs
* Pagination with valid values
* Invalid page values
* Invalid limit values
* Maximum limit validation
* Analytics endpoint responses

All implemented analytics endpoints were tested successfully with `200 OK` responses.

---

## Known Limitations

The Olist dataset contains incomplete boundary periods.

Some early and late months contain very few orders. As a result, monthly growth and YoY growth percentages can become extremely large or negative when compared with months containing very small order counts.

These values are mathematically correct based on the available dataset but should be interpreted with caution.

The category translation table contains fewer categories than the product dataset. Some product categories therefore do not have a corresponding translated category name.

---

## Dashboard

A Power BI dashboard was created to analyze Olist e-commerce sales, customer, order, product, payment, and delivery performance.

The dashboard includes:

* Total Revenue
* Total Orders
* Total Customers
* Average Order Value
* Monthly Revenue Trend
* Revenue by State
* Revenue by Product Category
* Top 10 Products by Revenue
* Top 10 Customers by Lifetime Value
* Payment Method Distribution
* Order Status Distribution
* Delivery Performance

Interactive filters include:

* Date
* State
* Category
* Payment Type

Dashboard deliverables:

* `olist_ecommerce_dashboard.pbix` — Power BI dashboard file
* `dashboard.png` — dashboard screenshot


---

## Technologies Used

* Python
* FastAPI
* SQLite
* Pandas
* SQL
* Uvicorn
* REST API
* Swagger / OpenAPI

---

## Candidate Assignment

The complete assessment instructions are available in:

**CANDIDATE_TASK.md**

Submission requirements are available in:

**SUBMISSION_GUIDELINES.md**
