-- a) Order totals = 180, total_revenue = 99860.20, avg_order_value = 554.78
SELECT 
    COUNT(*) AS total_orders,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0)/100)), 2) AS total_revenue,
    ROUND(AVG(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0)/100)), 2) AS avg_order_value
FROM orders o
JOIN products p 
    ON o.product_id = p.product_id;

-- b) COUNT(*) vs COUNT(column) - total_orders = 180, rated_orders = 165, unrated_orders = 15
SELECT 
    COUNT(*) AS total_orders,
    COUNT(rating) AS rated_orders,
    COUNT(*) - COUNT(rating) AS unrated_orders
FROM orders;

-- c) LEFT JOIN with a genuine zero-match row 
-- 1) Using LEFT JOIN + HAVING COUNT(order_id) = 0 - one customer with zero orders → C045, Vihaan
SELECT 
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o 
    ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;
-- LEFT JOIN with a genuine zero-match row
-- 2) Using NOT IN against orders - same result as above → C045, Vihaan
SELECT 
    c.customer_id,
    c.name
FROM customers c
WHERE c.customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders
);

--  d) GROUP BY + HAVING - Jaipur (19, 8, 42.1), Lucknow (49, 15, 30.6), Bangalore (33, 8, 24.2)
SELECT 
    c.city,
    COUNT(o.order_id) AS total_orders,
    SUM(o.returned) AS returned_orders,
    ROUND(100.0 * SUM(o.returned) / COUNT(o.order_id), 1) AS return_rate_pct
FROM orders o
JOIN customers c 
    ON o.customer_id = c.customer_id
GROUP BY c.city
HAVING ROUND(100.0 * SUM(o.returned) / COUNT(o.order_id), 1) > 20
ORDER BY return_rate_pct DESC;

-- e) Ranking with ORDER BY + LIMIT/OFFSET 
-- Using LIMIT - Top 5 spenders:
-- C043 Reyansh 12920.00
-- C026 Isha    8371.60
-- C008 Meera   4564.60
-- C011 Arjun   4111.00
-- C042 Sanya   3785.00
SELECT 
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0)/100)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;
-- Using OFFSET - last three spenders (3-5) of the above five spenders, in the same order:
-- C008 Meera   4564.60
-- C011 Arjun   4111.00
-- C042 Sanya   3785.00
SELECT 
    c.customer_id,
    c.name,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0)/100)), 2) AS total_spend
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- f) Three-table JOIN with GROUP BY - Haircare (54, 44956.10), Skincare (60, 27346.00), Babycare (30, 16805.00), PersonalCare (36, 10753.10)
SELECT 
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0)/100)), 2) AS category_revenue
FROM orders o
JOIN products p 
    ON o.product_id = p.product_id
JOIN customers c 
    ON o.customer_id = c.customer_id   -- included to confirm 3-way join compiles cleanly
GROUP BY p.category
ORDER BY category_revenue DESC;

-- g) LIKE pattern match - 10 rows (customers whose name starts with 'A')
SELECT
    customer_id,
	name
FROM customers
WHERE name LIKE 'A%';

-- h) DISTINCT (distinct acquisition_source values used across all customers) - 4 values — Ad, Organic, Referral, Social.
SELECT DISTINCT acquisition_source
FROM customers;

-- i) ALTER TABLE + UPDATE with CASE - Gold (28) and Silver (17)
-- Step 1: Add loyalty_tier column
ALTER TABLE customers
ADD loyalty_tier VARCHAR(10);
-- Step 2: Update every row with CASE logic
UPDATE customers
SET loyalty_tier = CASE 
    WHEN city_tier = 1 THEN 'Gold'
    ELSE 'Silver'
END;
-- Step 3: Verifying the distribution - Gold = 28, Silver = 17
SELECT 
    loyalty_tier,
    COUNT(*) AS customer_count
FROM customers
GROUP BY loyalty_tier;
