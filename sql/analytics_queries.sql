-- Olist E-commerce Analytics SQL Queries
-- Database: SQLite
-- Purpose: Business analytics queries used by the FastAPI analytics endpoints.
-------------------------------------------------------------------------------

-- Revenue definition:
--   Revenue = SUM(order_items.price)
--   freight_value is excluded.
-------------------------------

-- Valid sales orders:
--   Orders with status 'canceled' and 'unavailable' are excluded
--   from sales/revenue-related metrics.

-- ============================================================
-- 1. TOP 10 SELLING PRODUCTS
-- ============================================================

SELECT
oi.product_id,
COUNT(*) AS units_sold
FROM order_items oi
JOIN orders o
ON oi.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY oi.product_id
ORDER BY units_sold DESC
LIMIT 10;

-- ============================================================
-- 2. TOP 10 REVENUE-GENERATING PRODUCTS
-- ============================================================

SELECT
oi.product_id,
ROUND(SUM(oi.price), 2) AS revenue
FROM order_items oi
JOIN orders o
ON oi.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY oi.product_id
ORDER BY revenue DESC
LIMIT 10;

-- ============================================================
-- 3. MONTHLY REVENUE
-- ============================================================

SELECT
SUBSTR(o.order_purchase_timestamp, 7, 4)
|| '-' ||
SUBSTR(o.order_purchase_timestamp, 4, 2) AS month,
ROUND(SUM(oi.price), 2) AS revenue
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable')
GROUP BY month
ORDER BY month;

-- ============================================================
-- 4. REVENUE BY STATE
-- ============================================================

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
ORDER BY revenue DESC;

-- ============================================================
-- 5. REVENUE BY CATEGORY
-- ============================================================

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
ORDER BY revenue DESC;

-- ============================================================
-- 6. AVERAGE ORDER VALUE
-- ============================================================

SELECT
ROUND(
SUM(oi.price) / COUNT(DISTINCT o.order_id),
2
) AS average_order_value
FROM orders o
JOIN order_items oi
ON o.order_id = oi.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');

-- ============================================================
-- 7. AVERAGE DELIVERY TIME
-- ============================================================

SELECT
ROUND(
AVG(
julianday(
SUBSTR(o.order_delivered_customer_date, 7, 4)
|| '-' ||
SUBSTR(o.order_delivered_customer_date, 4, 2)
|| '-' ||
SUBSTR(o.order_delivered_customer_date, 1, 2)
)
-
julianday(
SUBSTR(o.order_purchase_timestamp, 7, 4)
|| '-' ||
SUBSTR(o.order_purchase_timestamp, 4, 2)
|| '-' ||
SUBSTR(o.order_purchase_timestamp, 1, 2)
)
),
2
) AS average_delivery_days
FROM orders o
WHERE o.order_delivered_customer_date IS NOT NULL;

-- ============================================================
-- 8. LATE DELIVERIES
-- ============================================================

SELECT
COUNT(*) AS late_deliveries
FROM orders
WHERE order_delivered_customer_date IS NOT NULL
AND order_estimated_delivery_date IS NOT NULL
AND julianday(
SUBSTR(order_delivered_customer_date, 7, 4)
|| '-' ||
SUBSTR(order_delivered_customer_date, 4, 2)
|| '-' ||
SUBSTR(order_delivered_customer_date, 1, 2)
)
>
julianday(
SUBSTR(order_estimated_delivery_date, 7, 4)
|| '-' ||
SUBSTR(order_estimated_delivery_date, 4, 2)
|| '-' ||
SUBSTR(order_estimated_delivery_date, 1, 2)
);

-- ============================================================
-- 9. TOP 20 CUSTOMERS BY LIFETIME VALUE
-- ============================================================

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
LIMIT 20;

-- ============================================================
-- 10. PAYMENT METHOD DISTRIBUTION
-- ============================================================

WITH payment_orders AS (
SELECT DISTINCT
order_id,
payment_type
FROM payments
)
SELECT
payment_type,
COUNT(DISTINCT order_id) AS order_count,
ROUND(
COUNT(DISTINCT order_id) * 100.0
/ (SELECT COUNT(DISTINCT order_id) FROM payments),
2
) AS percentage
FROM payment_orders
GROUP BY payment_type
ORDER BY order_count DESC;

-- ============================================================
-- 11. CANCELLATION RATE
-- ============================================================

SELECT
ROUND(
SUM(
CASE
WHEN order_status = 'canceled' THEN 1
ELSE 0
END
) * 100.0 / COUNT(*),
2
) AS cancellation_rate_percentage
FROM orders;

-- ============================================================
-- 12. REPEAT CUSTOMERS
-- ============================================================

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
COUNT(*) AS repeat_customers,
ROUND(
COUNT(*) * 100.0 /
(SELECT COUNT(*) FROM customer_orders),
2
) AS repeat_customer_percentage
FROM customer_orders
WHERE order_count > 1;

-- ============================================================
-- 13. AVERAGE BASKET SIZE
-- ============================================================

SELECT
ROUND(
COUNT(*) * 1.0 /
COUNT(DISTINCT o.order_id),
2
) AS average_basket_size
FROM order_items oi
JOIN orders o
ON oi.order_id = o.order_id
WHERE o.order_status NOT IN ('canceled', 'unavailable');

-- ============================================================
-- 14. MONTHLY ORDER GROWTH
-- ============================================================

WITH monthly_orders AS (
SELECT
SUBSTR(order_purchase_timestamp, 7, 4)
|| '-' ||
SUBSTR(order_purchase_timestamp, 4, 2) AS month,
COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE order_status NOT IN ('canceled', 'unavailable')
GROUP BY month
),
growth_calculation AS (
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
(order_count - previous_month_orders) * 100.0
/ previous_month_orders,
2
) AS growth_percentage
FROM growth_calculation
WHERE previous_month_orders IS NOT NULL
ORDER BY month;

-- ============================================================
-- 15. YEAR-OVER-YEAR ORDER GROWTH
-- ============================================================

WITH monthly_orders AS (
SELECT
SUBSTR(order_purchase_timestamp, 7, 4)
|| '-' ||
SUBSTR(order_purchase_timestamp, 4, 2) AS month,
COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE order_status NOT IN ('canceled', 'unavailable')
GROUP BY month
),
yoy_calculation AS (
SELECT
current.month,
current.order_count,
previous.order_count AS previous_year_orders
FROM monthly_orders current
LEFT JOIN monthly_orders previous
ON previous.month =
printf(
'%04d-%s',
CAST(SUBSTR(current.month, 1, 4) AS INTEGER) - 1,
SUBSTR(current.month, 6, 2)
)
)
SELECT
month,
order_count,
previous_year_orders,
ROUND(
(order_count - previous_year_orders) * 100.0
/ previous_year_orders,
2
) AS yoy_growth_percentage
FROM yoy_calculation
WHERE previous_year_orders IS NOT NULL
ORDER BY month;
