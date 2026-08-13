-- queries/where_having_combined.sql
-- Combining row filtering (WHERE) and group filtering (HAVING)
SELECT 
    c.customer_type,
    COUNT(DISTINCT t.customer_id) as segment_customers,
    SUM(t.amount) as segment_revenue,
    ROUND(AVG(t.amount), 2) as avg_order_value
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'          -- WHERE: data quality date range filter
  AND t.transaction_status = 'completed'           -- WHERE: filters only valid completed transactions
  AND t.amount > 0                                 -- WHERE: removes negative/zero refund records
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 10        -- HAVING: segment volume validation post-aggregation
  AND SUM(t.amount) > 100000                       -- HAVING: business threshold filter on aggregate revenue
ORDER BY segment_revenue DESC;
