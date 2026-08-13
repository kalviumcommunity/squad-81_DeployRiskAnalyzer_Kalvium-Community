-- Table: agg_daily_metrics
-- Purpose: Pre-aggregated dashboard table to serve historical daily metrics instantly
-- Grain: Daily aggregates per metric name
-- Refreshed: Periodic batch runs (daily or hourly)
-- Used by: Executive KPIs dashboard, daily monitoring
-- 
-- Columns:
--   aggregation_date: Calendar day of metrics
--   metric_name: Label distinguishing the KPI (e.g., total_revenue)
--   metric_value: Numeric value of the aggregated metric
--   row_count: Number of raw records compressed into this aggregate row
--   updated_at: Timestamp when the aggregation was calculated

CREATE TABLE agg_daily_metrics (
    aggregation_date DATE,
    metric_name VARCHAR(100),
    metric_value NUMERIC,
    row_count INTEGER,
    updated_at TIMESTAMP
);
