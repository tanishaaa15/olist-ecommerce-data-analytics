from fastapi import FastAPI, HTTPException, Header, Query
import sqlite3
import pandas as pd
from pathlib import Path

#FastAPI configuation
app = FastAPI(
    title="Olist Interview API",
    description="REST API for Data Analytics Interview",
    version="2.1"
)

# ----------------------------------------------------
# Configuration
# ----------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "olist.db"

API_KEY = "candidate-test-2026"

print(f"Database Path: {DB_PATH}")
print(f"Database Exists: {DB_PATH.exists()}")


# ----------------------------------------------------
# Authentication
# ----------------------------------------------------

def verify_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )


# ----------------------------------------------------
# Database Connection
# ----------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ----------------------------------------------------
# Convert dataframe to JSON-safe format
# ----------------------------------------------------

def dataframe_to_records(df):
    df = df.where(pd.notnull(df), None)
    return df.to_dict(orient="records")


# ----------------------------------------------------
# Generic Table Loader
# ----------------------------------------------------

def get_table(table: str, page: int = 1, limit: int = 100):

    try:

        conn = get_connection()

        offset = (page - 1) * limit

        total = int(
            pd.read_sql(
                f"SELECT COUNT(*) as total FROM {table}",
                conn
            ).iloc[0]["total"]
        )

        df = pd.read_sql(
            f"""
            SELECT *
            FROM {table}
            LIMIT {limit}
            OFFSET {offset}
            """,
            conn
        )

        conn.close()

        return {
            "page": int(page),
            "limit": int(limit),
            "total_records": total,
            "returned_records": int(len(df)),
            "has_next": bool(offset + limit < total),
            "data": dataframe_to_records(df)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ----------------------------------------------------
# Home
# ----------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Welcome to Olist Interview API",
        "version": "2.1"
    }


# ----------------------------------------------------
# Customers Endpoints
# ----------------------------------------------------

@app.get("/customers")
def customers(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("customers", page, limit)


# ----------------------------------------------------
# Candidate Endpoints
# ----------------------------------------------------
@app.get("/customers/{customer_id}")
def customer_by_id(
    customer_id: str,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    customer = pd.read_sql(
        "SELECT * FROM customers WHERE customer_id = ?",
        conn,
        params=(customer_id,)
    )

    conn.close()

    if customer.empty:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return dataframe_to_records(customer)[0]

# ----------------------------------------------------
# Orders endpoints
# ----------------------------------------------------

@app.get("/orders")
def orders(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("orders", page, limit)

# ----------------------------------------------------
# Order Endpoints
# ----------------------------------------------------
@app.get("/orders/{order_id}")
def order_by_id(
    order_id: str,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    order = pd.read_sql(
        "SELECT * FROM orders WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    conn.close()

    if order.empty:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return dataframe_to_records(order)[0]

# ----------------------------------------------------
# Order Items
# ----------------------------------------------------

@app.get("/order_items")
def order_items(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("order_items", page, limit)


# ----------------------------------------------------
# Payments
# ----------------------------------------------------

@app.get("/payments")
def payments(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("payments", page, limit)


# ----------------------------------------------------
# Products
# ----------------------------------------------------

@app.get("/products")
def products(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("products", page, limit)

@app.get("/products/{product_id}")
def product_by_id(
    product_id: str,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    product = pd.read_sql(
        "SELECT * FROM products WHERE product_id = ?",
        conn,
        params=(product_id,)
    )

    conn.close()

    if product.empty:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return dataframe_to_records(product)[0]


# ----------------------------------------------------
# Categories
# ----------------------------------------------------
@app.get("/categories")
def categories(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    offset = (page - 1) * limit

    total = pd.read_sql(
        """
        SELECT COUNT(DISTINCT product_category_name) AS total
        FROM products
        WHERE product_category_name IS NOT NULL
        """,
        conn
    ).iloc[0]["total"]

    categories_df = pd.read_sql(
        """
        SELECT DISTINCT product_category_name
        FROM products
        WHERE product_category_name IS NOT NULL
        ORDER BY product_category_name
        LIMIT ? OFFSET ?
        """,
        conn,
        params=(limit, offset)
    )

    conn.close()

    return {
        "page": page,
        "limit": limit,
        "total_records": int(total),
        "returned_records": len(categories_df),
        "has_next": bool(offset + limit < total),
        "data": dataframe_to_records(categories_df)
    }


@app.get("/categories/translation")
def category_translations(
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("category_translation", page, limit)



# ----------------------------------------------------
# Sellers
# ----------------------------------------------------

@app.get("/sellers")
def sellers(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("sellers", page, limit)


# ----------------------------------------------------
# Reviews
# ----------------------------------------------------

@app.get("/reviews")
def reviews(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("reviews", page, limit)


# ----------------------------------------------------
# Geolocation
# ----------------------------------------------------

@app.get("/geolocation")
def geolocation(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("geolocation", page, limit)


# ----------------------------------------------------
# Category Translation
# ----------------------------------------------------

@app.get("/category_translation")
def category_translation(
    page: int = 1,
    limit: int = 100,
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)
    return get_table("category_translation", page, limit)


# ----------------------------------------------------
# Order Details (Nested JSON)
# ----------------------------------------------------

@app.get("/orders/{order_id}/details")
def order_details(
    order_id: str,
    x_api_key: str = Header(None)
):

    verify_key(x_api_key)

    conn = get_connection()

    order = pd.read_sql(
        "SELECT * FROM orders WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    if order.empty:
        conn.close()
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    items = pd.read_sql(
        "SELECT * FROM order_items WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    payments = pd.read_sql(
        "SELECT * FROM payments WHERE order_id = ?",
        conn,
        params=(order_id,)
    )

    reviews = pd.read_sql(
        "SELECT * FROM reviews WHERE order_id = ?",
        conn,
        params=(order_id,)
    )
# Close the database connection after retrieving the data. 
    conn.close() 
# Return the order and its related records as nested JSON. 
    return { "order": dataframe_to_records(order)[0], 
            "items": dataframe_to_records(items), 
            "payments": dataframe_to_records(payments), 
            "reviews": dataframe_to_records(reviews) }

#ANALYTICS ENDPOINTS 


#Top selling products
@app.get("/analytics/top-selling-products")
def top_selling_products(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        oi.product_id,
        COUNT(*) AS units_sold
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY oi.product_id
    ORDER BY units_sold DESC
    LIMIT 10
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


# Top Revenue-Generating Products
@app.get("/analytics/top-revenue-products")
def top_revenue_products(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        oi.product_id,
        ROUND(SUM(oi.price), 2) AS revenue
    FROM order_items oi
    JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY oi.product_id
    ORDER BY revenue DESC
    LIMIT 10
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


# Monthly Revenue
@app.get("/analytics/monthly-revenue")
def monthly_revenue(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        SUBSTR(o.order_purchase_timestamp, 7, 4) || '-' ||
        SUBSTR(o.order_purchase_timestamp, 4, 2) AS month,
        ROUND(SUM(oi.price), 2) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY month
    ORDER BY month
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)

# Revenue by State
@app.get("/analytics/revenue-by-state")
def revenue_by_state(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        c.customer_state AS state,
        ROUND(SUM(oi.price), 2) AS revenue
    FROM orders o
    JOIN customers c
        ON o.customer_id = c.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_state
    ORDER BY revenue DESC
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


# Revenue by Category
@app.get("/analytics/revenue-by-category")
def revenue_by_category(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        p.product_category_name AS category,
        ROUND(SUM(oi.price), 2) AS revenue
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    JOIN products p
        ON oi.product_id = p.product_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
        AND p.product_category_name IS NOT NULL
    GROUP BY p.product_category_name
    ORDER BY revenue DESC
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


# Average Order Value
@app.get("/analytics/average-order-value")
def average_order_value(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        ROUND(
            SUM(oi.price) /
            COUNT(DISTINCT o.order_id),
            2
        ) AS average_order_value
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


# Average Delivery Time
@app.get("/analytics/average-delivery-time")
def average_delivery_time(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        ROUND(
            AVG(
                julianday(
                    substr(o.order_delivered_customer_date, 7, 4) || '-' ||
                    substr(o.order_delivered_customer_date, 4, 2) || '-' ||
                    substr(o.order_delivered_customer_date, 1, 2) || ' ' ||
                    substr(o.order_delivered_customer_date, 12)
                )
                -
                julianday(
                    substr(o.order_purchase_timestamp, 7, 4) || '-' ||
                    substr(o.order_purchase_timestamp, 4, 2) || '-' ||
                    substr(o.order_purchase_timestamp, 1, 2) || ' ' ||
                    substr(o.order_purchase_timestamp, 12)
                )
            ),
            2
        ) AS average_delivery_days
    FROM orders o
    WHERE o.order_status = 'delivered'
        AND o.order_delivered_customer_date IS NOT NULL
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)



#Late Deliveries
@app.get("/analytics/late-deliveries")
def late_deliveries(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        COUNT(*) AS late_deliveries
    FROM orders o
    WHERE o.order_status = 'delivered'
        AND o.order_delivered_customer_date IS NOT NULL
        AND o.order_estimated_delivery_date IS NOT NULL
        AND julianday(
            substr(o.order_delivered_customer_date, 7, 4) || '-' ||
            substr(o.order_delivered_customer_date, 4, 2) || '-' ||
            substr(o.order_delivered_customer_date, 1, 2) || ' ' ||
            substr(o.order_delivered_customer_date, 12)
        )
        >
        julianday(
            substr(o.order_estimated_delivery_date, 7, 4) || '-' ||
            substr(o.order_estimated_delivery_date, 4, 2) || '-' ||
            substr(o.order_estimated_delivery_date, 1, 2)
        )
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


#Top 20 Customers by Lifetime Value
@app.get("/analytics/top-customers-lifetime-value")
def top_customers_lifetime_value(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        c.customer_unique_id,
        ROUND(SUM(oi.price), 2) AS lifetime_value
    FROM customers c
    JOIN orders o
        ON c.customer_id = o.customer_id
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY c.customer_unique_id
    ORDER BY lifetime_value DESC
    LIMIT 20
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


#Payment Method Distribution
@app.get("/analytics/payment-method-distribution")
def payment_method_distribution(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        p.payment_type,
        COUNT(DISTINCT p.order_id) AS order_count,
        ROUND(
            COUNT(DISTINCT p.order_id) * 100.0 /
            (
                SELECT COUNT(DISTINCT order_id)
                FROM payments
            ),
            2
        ) AS percentage
    FROM payments p
    GROUP BY p.payment_type
    ORDER BY order_count DESC
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


#Cancellation Rate
@app.get("/analytics/cancellation-rate")
def cancellation_rate(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        COUNT(CASE WHEN order_status = 'canceled' THEN 1 END) AS canceled_orders,
        COUNT(*) AS total_orders,
        ROUND(
            COUNT(CASE WHEN order_status = 'canceled' THEN 1 END)
            * 100.0 / COUNT(*),
            2
        ) AS cancellation_rate_percentage
    FROM orders
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


#Repeat Customers
@app.get("/analytics/repeat-customers")
def repeat_customers(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    WITH customer_orders AS (
        SELECT
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS order_count
        FROM customers c
        JOIN orders o
            ON c.customer_id = o.customer_id
        GROUP BY c.customer_unique_id
    )
    SELECT
        COUNT(*) AS total_customers,
        SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END) AS repeat_customers,
        ROUND(
            SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
            * 100.0 / COUNT(*),
            2
        ) AS repeat_customer_percentage
    FROM customer_orders
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


#Average Basket Size
@app.get("/analytics/average-basket-size")
def average_basket_size(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    SELECT
        ROUND(
            COUNT(oi.order_id) * 1.0 /
            COUNT(DISTINCT o.order_id),
            2
        ) AS average_basket_size
    FROM orders o
    JOIN order_items oi
        ON o.order_id = oi.order_id
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)


# Monthly Order Growth %
@app.get("/analytics/monthly-order-growth")
def monthly_order_growth(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    WITH monthly_orders AS (
        SELECT
            SUBSTR(order_purchase_timestamp, 7, 4) || '-' ||
            SUBSTR(order_purchase_timestamp, 4, 2) AS month,
            COUNT(DISTINCT order_id) AS order_count
        FROM orders
        WHERE order_status NOT IN ('canceled', 'unavailable')
        GROUP BY month
    ),
    monthly_with_previous AS (
        SELECT
            month,
            order_count,
            LAG(order_count) OVER (
                ORDER BY month
            ) AS previous_month_orders
        FROM monthly_orders
    )
    SELECT
        month,
        order_count,
        previous_month_orders,
        ROUND(
            (
                order_count - previous_month_orders
            ) * 100.0 / previous_month_orders,
            2
        ) AS growth_percentage
    FROM monthly_with_previous
    WHERE previous_month_orders IS NOT NULL
        AND previous_month_orders > 0
    ORDER BY month
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)



# YoY Growth
@app.get("/analytics/yoy-growth")
def yoy_growth(
    x_api_key: str = Header(None)
):
    verify_key(x_api_key)

    conn = get_connection()

    query = """
    WITH monthly_orders AS (
        SELECT
            SUBSTR(order_purchase_timestamp, 7, 4) || '-' ||
            SUBSTR(order_purchase_timestamp, 4, 2) AS month,
            SUBSTR(order_purchase_timestamp, 7, 4) AS year,
            SUBSTR(order_purchase_timestamp, 4, 2) AS month_number,
            COUNT(DISTINCT order_id) AS order_count
        FROM orders
        WHERE order_status NOT IN ('canceled', 'unavailable')
        GROUP BY month
    )
    SELECT
        current.month,
        current.order_count,
        previous.order_count AS previous_year_orders,
        ROUND(
            (
                current.order_count - previous.order_count
            ) * 100.0 / previous.order_count,
            2
        ) AS yoy_growth_percentage
    FROM monthly_orders current
    JOIN monthly_orders previous
        ON current.month_number = previous.month_number
        AND CAST(current.year AS INTEGER) =
            CAST(previous.year AS INTEGER) + 1
    ORDER BY current.month
    """

    result = pd.read_sql(query, conn)

    conn.close()

    return dataframe_to_records(result)