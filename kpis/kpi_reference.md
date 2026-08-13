# KPI Reference Document

This document serves as the single source of truth for our key performance indicators (KPIs) to align Finance, Sales, Product, and executive teams.

---

## 1. Monthly Active Users (MAU)
* **Definition**: Distinct customers with at least one transaction in the last 30 days.
* **Formula**: `COUNT(DISTINCT customer_id) WHERE transaction_date >= TODAY() - 30 days`
* **Data Source**: `sales.csv` (columns: `customer_id`, `transaction_date`)
* **Target Range**: 5,000 - 6,000
* **Owner**: Product Manager
* **Update Frequency**: Daily
* **Notes**: Indicator of product engagement; seasonal dips in Q4.

---

## 2. Revenue per Customer (RPC)
* **Definition**: Average revenue generated per unique active customer.
* **Formula**: `SUM(amount) / COUNT(DISTINCT customer_id)`
* **Data Source**: `sales.csv` (columns: `amount`, `customer_id`)
* **Target Range**: $90.00 - $110.00
* **Owner**: Finance Director
* **Update Frequency**: Monthly
* **Notes**: Measures monetization efficiency and average ticket size.

---

## 3. Monthly Churn Rate
* **Definition**: The percentage of customers active in the previous 30-day period who had no transaction activity in the current 30-day period.
* **Formula**: `(Active_P1_Customers - Active_P2_Customers_Who_Were_Active_P1) / Active_P1_Customers`
* **Data Source**: `sales.csv` (columns: `customer_id`, `transaction_date`)
* **Target Range**: 0.0% - 5.0%
* **Owner**: Customer Success VP
* **Update Frequency**: Monthly
* **Notes**: Key metric for retention health. Spikes indicate potential onboarding or service quality issues.

---

## 4. Payment Success Rate
* **Definition**: The percentage of transactions that completed successfully without error or refusal.
* **Formula**: `COUNT(transaction_id WHERE status == 'Success') / TOTAL(transaction_id)`
* **Data Source**: `sales.csv` (columns: `transaction_id`, `payment_method`)
* **Target Range**: 95.0% - 100.0%
* **Owner**: Operations Lead
* **Update Frequency**: Daily
* **Notes**: Monitors payment gateway performance and checkout friction.

---

## 5. Customer Acquisition Cost (CAC)
* **Definition**: The average cost incurred to acquire a single new paying customer.
* **Formula**: `Total Marketing and Sales Expenses / Number of New Customers Acquired`
* **Data Source**: Marketing budget & transaction history
* **Target Range**: $0.00 - $50.00
* **Owner**: Marketing Director
* **Update Frequency**: Monthly
* **Notes**: Needs to be compared against LTV to evaluate funnel health.
