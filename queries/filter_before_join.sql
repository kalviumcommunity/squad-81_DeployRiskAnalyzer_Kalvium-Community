-- queries/filter_before_join.sql
-- Optimized version: Filter transactions BEFORE joining
WITH filtered_trans AS (
    SELECT transaction_id, customer_id, product_id, amount, transaction_date
    FROM transactions
    WHERE transaction_date >= '2024-01-01'
      AND amount > 100
)
SELECT 
    ft.transaction_id, 
    ft.amount, 
    c.customer_name, 
    p.product_name
FROM filtered_trans ft
JOIN customers c ON ft.customer_id = c.id
JOIN products p ON ft.product_id = p.id
WHERE c.country = 'USA'
LIMIT 5000;
