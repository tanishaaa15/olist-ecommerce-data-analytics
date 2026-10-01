import sqlite3

conn = sqlite3.connect("olist.db")

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

row = conn.execute(query).fetchone()

print("\nAverage Delivery Time:", row[0], "days")

conn.close()