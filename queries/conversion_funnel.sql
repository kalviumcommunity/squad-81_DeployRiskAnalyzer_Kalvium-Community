-- queries/conversion_funnel.sql
-- Daily signup funnel conversion metrics
SELECT 
    strftime('%Y-%m-%d', u.created_at) as signup_date,
    COUNT(*) as signups,
    COUNT(CASE WHEN u.email_verified_at IS NOT NULL THEN 1 END) as email_verified,
    COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END) as first_purchase,
    ROUND(100.0 * COUNT(CASE WHEN u.first_purchase_at IS NOT NULL THEN 1 END) / COUNT(*), 1) as conversion_pct
FROM users u
WHERE u.created_at >= date('now', '-90 days')
GROUP BY signup_date
ORDER BY signup_date DESC;
