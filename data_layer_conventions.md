# Clean Data Layer Naming Conventions

This document outlines the database object naming standards and validation guidelines applied to the clean analytical layer in this repository.

## 1. Views
* **Prefix**: `vw_`
* **Pattern**: `vw_[business_entity]_[metric_scope]`
* **Examples**:
  * `vw_active_customers`: Aggregates active rolling 30-day indicators per customer entity.
  * `vw_your_custom_metric` (mapped as `vw_product_performance`): Aggregates sales volume, revenue contributions, and order instances per product SKU.

## 2. Pre-Aggregated Tables
* **Prefix**: `agg_`
* **Pattern**: `agg_[grain]_[metric_scope]`
* **Examples**:
  * `agg_daily_metrics`: Stores pre-aggregated daily KPI metric values (such as daily total revenue).

## 3. Columns in Aggregated Tables
* Always include `updated_at` or `created_at` timestamp.
* Always include `row_count` to audit the underlying transaction multiplier.
* Always include the aggregation temporal grain column (e.g. `aggregation_date`).

---

## 4. Answers to Follow-Up Questions

### Question 1: Dashboard Propagation on View Definition Change
* **Do existing dashboards automatically use the new definition?**
  * **Yes**. When a database view definition is modified (e.g. via `CREATE OR REPLACE VIEW`), the view's definition is updated in the database system catalog. Because dashboards query the view name dynamically (`SELECT * FROM vw_active_customers`) rather than caching the query plans, the database compiler parses the updated view definition on the next query call, returning the new schema/metrics automatically to all connected dashboards without requiring dashboard modifications.

### Question 2: Real-time Metric Handling and Refresh Latency
* **What happens to data between refresh cycles?**
  * When an aggregated table is computed on an hourly basis, any transaction occurring between cycles is missing from the dashboard, leading to an hourly reporting lag.
* **How to handle real-time metrics**:
  * We can use a **Lambda Architecture** or **Hybrid Query Pattern**:
    ```sql
    -- Query the pre-aggregated summary table for historical data, 
    -- unioned with a live scan of raw transactions occurring only since the last batch refresh.
    SELECT aggregation_date, SUM(metric_value) FROM agg_daily_metrics
    UNION ALL
    SELECT date(order_date), SUM(order_amount) 
    FROM orders 
    WHERE order_date >= (SELECT MAX(updated_at) FROM agg_daily_metrics);
    ```

### Question 3: Pre-release Correctness Testing
To test the accuracy of a view or aggregated table before exposing it:
1. **Row count validation**: Confirm that the sum of `row_count` in the aggregated table matches the count in the raw transactions table.
2. **Deterministic aggregate checks**: Run a test query summing all values on the raw table and compare it directly to the sum on the clean view:
   `SUM(order_amount) FROM orders` vs `SUM(revenue_30d) FROM vw_active_customers`.
3. **Boundary Value Testing**: Verify that records at the temporal edges (exactly 30 days ago, or at midnight boundaries) are captured correctly without double counting.
