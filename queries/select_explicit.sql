-- queries/select_explicit.sql
-- Optimized version: Explicit columns instead of SELECT *
SELECT 
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.customer_id,
    c.customer_name,
    c.country,
    c.account_type
FROM transactions t
JOIN customers c ON t.customer_id = c.id
WHERE strftime('%Y', t.transaction_date) = '2024'
LIMIT 1000;
