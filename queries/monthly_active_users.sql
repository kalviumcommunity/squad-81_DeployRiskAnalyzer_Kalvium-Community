-- queries/monthly_active_users.sql
-- Monthly Active Users with Segment breakdown
SELECT 
    strftime('%Y-%m-01', transaction_date) as month,
    COUNT(DISTINCT customer_id) as active_users,
    COUNT(DISTINCT CASE WHEN customer_type='Enterprise' THEN customer_id END) as enterprise_users,
    COUNT(DISTINCT CASE WHEN customer_type='SMB' THEN customer_id END) as smb_users
FROM transactions
WHERE transaction_date >= date('now', '-12 months')
GROUP BY month
ORDER BY month DESC;
