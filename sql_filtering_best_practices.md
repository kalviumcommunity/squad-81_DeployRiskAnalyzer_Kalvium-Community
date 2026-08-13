# SQL Filtering Best Practices: WHERE vs HAVING

Understanding when to filter data in SQL is critical for both query correctness and performance. This guide documents the correct usage patterns for the team.

## Summary: The Core Difference

| Feature | `WHERE` | `HAVING` |
|---|---|---|
| **Execution Order** | Executes **BEFORE** data grouping (`GROUP BY`). | Executes **AFTER** data grouping (`GROUP BY`). |
| **Target Level** | Filters individual **rows** of data. | Filters aggregated **groups** of data. |
| **Aggregate Functions** | **Cannot** contain aggregate functions (e.g. `SUM`, `AVG`, `COUNT`). | **Can** contain aggregate functions. |
| **Primary Use Case** | Data cleaning, filtering invalid states, date range limits. | Filtering aggregated segments based on sizes or value limits. |

---

## 1. WHERE: Filtering Before Grouping
Use `WHERE` to discard irrelevant rows before any aggregation takes place. This reduces database workload.

```sql
SELECT customer_id, SUM(amount) as revenue
FROM transactions
WHERE transaction_status = 'completed'  -- Discard failed transactions first
GROUP BY customer_id;
```

---

## 2. HAVING: Filtering Groups After Aggregation
Use `HAVING` to filter groups based on aggregated calculations (e.g., total sales, customer counts).

```sql
SELECT customer_id, SUM(amount) as revenue
FROM transactions
GROUP BY customer_id
HAVING SUM(amount) > 10000;            -- Filter cohorts that spent > $10k
```

---

## 3. Combining WHERE and HAVING (Recommended Pattern)
In production, queries should combine both:
1. `WHERE` filters out row-level anomalies (refunds, date boundaries, incomplete records).
2. `GROUP BY` aggregates the clean rows.
3. `HAVING` filters the resulting cohort sizes or sum thresholds.

```sql
SELECT 
    c.customer_type,
    SUM(t.amount) as segment_revenue
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
WHERE t.transaction_date >= '2024-01-01'      -- WHERE: row filter
  AND t.transaction_status = 'completed'       -- WHERE: row filter
GROUP BY c.customer_type
HAVING COUNT(DISTINCT t.customer_id) >= 10;    -- HAVING: group size filter
```
