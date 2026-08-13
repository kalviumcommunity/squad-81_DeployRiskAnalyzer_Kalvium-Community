-- queries/having_filtering.sql
-- Filter GROUPS after aggregation using HAVING
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(amount) as annual_revenue
FROM transactions
WHERE transaction_date >= '2024-01-01'           -- WHERE: filters individual row records before grouping
GROUP BY customer_id
HAVING SUM(amount) > 10000                      -- HAVING: filters computed groups after sum aggregation
  AND COUNT(*) >= 5                             -- HAVING: only returns groups with 5+ transactions
ORDER BY annual_revenue DESC;
