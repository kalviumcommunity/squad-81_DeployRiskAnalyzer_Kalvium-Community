-- queries/unmatched_keys_orders.sql
-- Orders with NO matching customer (orphaned records)
SELECT o.order_id, o.customer_id, o.order_date
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
