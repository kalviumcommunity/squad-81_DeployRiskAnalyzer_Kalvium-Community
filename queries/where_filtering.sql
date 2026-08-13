-- queries/where_filtering.sql
-- Filter data quality issues BEFORE grouping
SELECT 
    customer_id,
    SUM(amount) as annual_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= '2024-01-01'           -- Date range filter (removes older records)
  AND amount > 0                                 -- Remove refunds or invalid zero amounts
  AND transaction_status = 'completed'           -- Only count completed / successful transactions
GROUP BY customer_id
ORDER BY annual_revenue DESC;
