# AEP Query Service Examples

Comprehensive SQL query examples for Adobe Experience Platform Query Service.

## Query Service Overview

Adobe Experience Platform Query Service enables standard SQL queries against data lake datasets, Real-Time Customer Profile, and ExperienceEvent data.

### Key Features

- **Standard SQL**: ANSI SQL with PostgreSQL extensions
- **Interactive Queries**: Fast queries (<10 min) for exploration
- **Scheduled Queries**: Recurring queries for reports and data preparation
- **CTAS (Create Table As Select)**: Materialize query results as datasets

## Basic Profile Queries

### 1. Count Total Profiles

```sql
-- Count all profiles in a dataset
SELECT COUNT(*) as total_profiles
FROM profile_dataset;
```

### 2. List Recent Profiles

```sql
-- Get most recently created profiles
SELECT
  personalEmail.address as email,
  person.name.firstName as first_name,
  person.name.lastName as last_name,
  _repo.createDate as created_at
FROM profile_dataset
ORDER BY _repo.createDate DESC
LIMIT 100;
```

### 3. Filter by Email Domain

```sql
-- Find all Gmail users
SELECT
  personalEmail.address as email,
  person.name.firstName || ' ' || person.name.lastName as full_name,
  homeAddress.city as city
FROM profile_dataset
WHERE personalEmail.address LIKE '%@gmail.com'
  AND personalEmail.status = 'active'
ORDER BY _repo.createDate DESC;
```

### 4. Geographic Distribution

```sql
-- Count profiles by city
SELECT
  homeAddress.city as city,
  homeAddress.stateProvince as state,
  COUNT(*) as customer_count
FROM profile_dataset
WHERE homeAddress.city IS NOT NULL
GROUP BY homeAddress.city, homeAddress.stateProvince
ORDER BY customer_count DESC
LIMIT 50;
```

### 5. Age Demographics

```sql
-- Calculate age distribution
SELECT
  CASE
    WHEN age < 18 THEN 'Under 18'
    WHEN age BETWEEN 18 AND 24 THEN '18-24'
    WHEN age BETWEEN 25 AND 34 THEN '25-34'
    WHEN age BETWEEN 35 AND 44 THEN '35-44'
    WHEN age BETWEEN 45 AND 54 THEN '45-54'
    WHEN age BETWEEN 55 AND 64 THEN '55-64'
    ELSE '65+'
  END as age_group,
  COUNT(*) as count
FROM (
  SELECT
    EXTRACT(YEAR FROM CURRENT_DATE) - EXTRACT(YEAR FROM person.birthDate::DATE) as age
  FROM profile_dataset
  WHERE person.birthDate IS NOT NULL
) age_calc
GROUP BY age_group
ORDER BY age_group;
```

## ExperienceEvent Queries

### 6. Recent Website Activity

```sql
-- Get page views from last 7 days
SELECT
  timestamp,
  web.webPageDetails.URL as page_url,
  web.webPageDetails.name as page_name,
  web.webReferrer.URL as referrer
FROM experience_event_dataset
WHERE eventType = 'web.webpagedetails.pageViews'
  AND timestamp >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY timestamp DESC
LIMIT 1000;
```

### 7. Purchase Analysis

```sql
-- Analyze purchases by day
SELECT
  DATE_TRUNC('day', timestamp) as purchase_date,
  COUNT(*) as total_orders,
  SUM(commerce.order.priceTotal) as total_revenue,
  AVG(commerce.order.priceTotal) as avg_order_value,
  COUNT(DISTINCT identityMap['email'][0].id) as unique_customers
FROM experience_event_dataset
WHERE eventType = 'commerce.purchases'
  AND timestamp >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY purchase_date
ORDER BY purchase_date DESC;
```

### 8. Product Performance

```sql
-- Top selling products
SELECT
  item.SKU as product_sku,
  item.name as product_name,
  COUNT(*) as times_purchased,
  SUM(item.quantity) as total_quantity,
  SUM(item.priceTotal) as total_revenue
FROM experience_event_dataset,
  UNNEST(productListItems) as item
WHERE eventType = 'commerce.purchases'
  AND timestamp >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY item.SKU, item.name
ORDER BY total_revenue DESC
LIMIT 20;
```

### 9. Shopping Cart Abandonment

```sql
-- Identify cart abandonment events
WITH cart_adds AS (
  SELECT
    identityMap['ECID'][0].id as visitor_id,
    DATE_TRUNC('day', timestamp) as event_date,
    COUNT(*) as add_to_cart_count
  FROM experience_event_dataset
  WHERE eventType = 'commerce.productListAdds'
    AND timestamp >= CURRENT_DATE - INTERVAL '7' DAY
  GROUP BY visitor_id, event_date
),
purchases AS (
  SELECT
    identityMap['ECID'][0].id as visitor_id,
    DATE_TRUNC('day', timestamp) as event_date,
    COUNT(*) as purchase_count
  FROM experience_event_dataset
  WHERE eventType = 'commerce.purchases'
    AND timestamp >= CURRENT_DATE - INTERVAL '7' DAY
  GROUP BY visitor_id, event_date
)
SELECT
  ca.event_date,
  ca.visitor_id,
  ca.add_to_cart_count,
  COALESCE(p.purchase_count, 0) as purchase_count
FROM cart_adds ca
LEFT JOIN purchases p
  ON ca.visitor_id = p.visitor_id
  AND ca.event_date = p.event_date
WHERE COALESCE(p.purchase_count, 0) = 0
ORDER BY ca.event_date DESC;
```

### 10. User Journey Analysis

```sql
-- Track user journey from first visit to purchase
WITH first_visit AS (
  SELECT
    identityMap['email'][0].id as email,
    MIN(timestamp) as first_visit_time
  FROM experience_event_dataset
  WHERE eventType = 'web.webpagedetails.pageViews'
  GROUP BY email
),
first_purchase AS (
  SELECT
    identityMap['email'][0].id as email,
    MIN(timestamp) as first_purchase_time,
    commerce.order.priceTotal as first_order_value
  FROM experience_event_dataset
  WHERE eventType = 'commerce.purchases'
  GROUP BY email, commerce.order.priceTotal
)
SELECT
  fv.email,
  fv.first_visit_time,
  fp.first_purchase_time,
  fp.first_order_value,
  EXTRACT(EPOCH FROM (fp.first_purchase_time - fv.first_visit_time)) / 3600 as hours_to_purchase
FROM first_visit fv
JOIN first_purchase fp ON fv.email = fp.email
WHERE fp.first_purchase_time > fv.first_visit_time
ORDER BY hours_to_purchase
LIMIT 100;
```

## Combined Profile + Event Queries

### 11. Customer Lifetime Value

```sql
-- Calculate CLV per customer
SELECT
  p.personalEmail.address as email,
  p.person.name.firstName || ' ' || p.person.name.lastName as customer_name,
  COUNT(DISTINCT e.commerce.order.purchaseID) as total_orders,
  SUM(e.commerce.order.priceTotal) as lifetime_value,
  MIN(e.timestamp) as first_purchase,
  MAX(e.timestamp) as last_purchase
FROM profile_dataset p
JOIN experience_event_dataset e
  ON p.personalEmail.address = e.identityMap['email'][0].id
WHERE e.eventType = 'commerce.purchases'
GROUP BY p.personalEmail.address, customer_name
HAVING COUNT(DISTINCT e.commerce.order.purchaseID) > 0
ORDER BY lifetime_value DESC
LIMIT 100;
```

### 12. Segment Membership Analysis

```sql
-- Customers who match specific criteria
SELECT
  p.personalEmail.address as email,
  p.person.name.firstName as first_name,
  p.homeAddress.city as city,
  COUNT(e._id) as purchase_count,
  SUM(e.commerce.order.priceTotal) as total_spent
FROM profile_dataset p
LEFT JOIN experience_event_dataset e
  ON p.personalEmail.address = e.identityMap['email'][0].id
  AND e.eventType = 'commerce.purchases'
  AND e.timestamp >= CURRENT_DATE - INTERVAL '90' DAY
WHERE p.homeAddress.countryCode = 'US'
  AND p.personalEmail.status = 'active'
GROUP BY p.personalEmail.address, first_name, city
HAVING COUNT(e._id) >= 3
ORDER BY total_spent DESC;
```

### 13. Churn Risk Analysis

```sql
-- Identify at-risk customers (no activity in 60 days)
SELECT
  p.personalEmail.address as email,
  p.person.name.firstName || ' ' || p.person.name.lastName as customer_name,
  MAX(e.timestamp) as last_activity,
  CURRENT_DATE - DATE(MAX(e.timestamp)) as days_since_activity,
  COUNT(DISTINCT e._id) as historical_event_count
FROM profile_dataset p
JOIN experience_event_dataset e
  ON p.personalEmail.address = e.identityMap['email'][0].id
WHERE e.timestamp >= CURRENT_DATE - INTERVAL '180' DAY
GROUP BY p.personalEmail.address, customer_name
HAVING MAX(e.timestamp) < CURRENT_DATE - INTERVAL '60' DAY
  AND COUNT(DISTINCT e._id) >= 5  -- Previously active users
ORDER BY days_since_activity DESC;
```

## Advanced Queries

### 14. Funnel Analysis

```sql
-- Conversion funnel from view to purchase
WITH funnel_events AS (
  SELECT
    identityMap['ECID'][0].id as visitor_id,
    DATE_TRUNC('day', timestamp) as event_date,
    MAX(CASE WHEN eventType = 'commerce.productViews' THEN 1 ELSE 0 END) as viewed_product,
    MAX(CASE WHEN eventType = 'commerce.productListAdds' THEN 1 ELSE 0 END) as added_to_cart,
    MAX(CASE WHEN eventType = 'commerce.checkouts' THEN 1 ELSE 0 END) as started_checkout,
    MAX(CASE WHEN eventType = 'commerce.purchases' THEN 1 ELSE 0 END) as completed_purchase
  FROM experience_event_dataset
  WHERE timestamp >= CURRENT_DATE - INTERVAL '7' DAY
  GROUP BY visitor_id, event_date
)
SELECT
  SUM(viewed_product) as step1_product_views,
  SUM(added_to_cart) as step2_add_to_cart,
  SUM(started_checkout) as step3_checkout,
  SUM(completed_purchase) as step4_purchase,
  ROUND(100.0 * SUM(added_to_cart) / NULLIF(SUM(viewed_product), 0), 2) as view_to_cart_rate,
  ROUND(100.0 * SUM(started_checkout) / NULLIF(SUM(added_to_cart), 0), 2) as cart_to_checkout_rate,
  ROUND(100.0 * SUM(completed_purchase) / NULLIF(SUM(started_checkout), 0), 2) as checkout_to_purchase_rate
FROM funnel_events;
```

### 15. RFM Segmentation (Recency, Frequency, Monetary)

```sql
-- Calculate RFM scores for customer segmentation
WITH customer_metrics AS (
  SELECT
    identityMap['email'][0].id as email,
    MAX(timestamp) as last_purchase_date,
    COUNT(DISTINCT commerce.order.purchaseID) as purchase_frequency,
    SUM(commerce.order.priceTotal) as monetary_value
  FROM experience_event_dataset
  WHERE eventType = 'commerce.purchases'
    AND timestamp >= CURRENT_DATE - INTERVAL '365' DAY
  GROUP BY email
),
rfm_scores AS (
  SELECT
    email,
    CURRENT_DATE - DATE(last_purchase_date) as recency_days,
    purchase_frequency,
    monetary_value,
    NTILE(5) OVER (ORDER BY last_purchase_date DESC) as recency_score,
    NTILE(5) OVER (ORDER BY purchase_frequency ASC) as frequency_score,
    NTILE(5) OVER (ORDER BY monetary_value ASC) as monetary_score
  FROM customer_metrics
)
SELECT
  email,
  recency_days,
  purchase_frequency,
  monetary_value,
  recency_score,
  frequency_score,
  monetary_score,
  recency_score + frequency_score + monetary_score as rfm_total,
  CASE
    WHEN recency_score >= 4 AND frequency_score >= 4 AND monetary_score >= 4 THEN 'Champions'
    WHEN recency_score >= 3 AND frequency_score >= 3 THEN 'Loyal Customers'
    WHEN recency_score >= 4 AND frequency_score <= 2 THEN 'Promising'
    WHEN recency_score <= 2 AND frequency_score >= 3 THEN 'At Risk'
    WHEN recency_score <= 2 AND frequency_score <= 2 THEN 'Lost'
    ELSE 'Others'
  END as customer_segment
FROM rfm_scores
ORDER BY rfm_total DESC;
```

### 16. Session Analysis

```sql
-- Define and analyze user sessions (30 min timeout)
WITH session_events AS (
  SELECT
    identityMap['ECID'][0].id as visitor_id,
    timestamp,
    web.webPageDetails.URL as page_url,
    LAG(timestamp) OVER (PARTITION BY identityMap['ECID'][0].id ORDER BY timestamp) as prev_timestamp
  FROM experience_event_dataset
  WHERE eventType = 'web.webpagedetails.pageViews'
    AND timestamp >= CURRENT_DATE - INTERVAL '7' DAY
),
sessions AS (
  SELECT
    visitor_id,
    timestamp,
    page_url,
    SUM(CASE
      WHEN prev_timestamp IS NULL OR
           EXTRACT(EPOCH FROM (timestamp - prev_timestamp)) > 1800
      THEN 1 ELSE 0
    END) OVER (PARTITION BY visitor_id ORDER BY timestamp) as session_id
  FROM session_events
)
SELECT
  DATE_TRUNC('day', MIN(timestamp)) as session_date,
  COUNT(DISTINCT visitor_id || '_' || session_id) as total_sessions,
  AVG(page_count) as avg_pages_per_session,
  AVG(session_duration_seconds) / 60.0 as avg_session_duration_minutes
FROM (
  SELECT
    visitor_id,
    session_id,
    COUNT(*) as page_count,
    EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) as session_duration_seconds,
    MIN(timestamp) as session_start
  FROM sessions
  GROUP BY visitor_id, session_id
) session_stats
GROUP BY session_date
ORDER BY session_date DESC;
```

## CTAS (Create Table As Select)

### 17. Create Derived Dataset

```sql
-- Create a materialized customer summary table
CREATE TABLE customer_summary_30d AS
SELECT
  p.personalEmail.address as email,
  p.person.name.firstName as first_name,
  p.person.name.lastName as last_name,
  p.homeAddress.city as city,
  p.homeAddress.stateProvince as state,
  COUNT(DISTINCT e._id) as total_events,
  COUNT(DISTINCT CASE WHEN e.eventType = 'commerce.purchases' THEN e._id END) as purchase_count,
  SUM(CASE WHEN e.eventType = 'commerce.purchases' THEN e.commerce.order.priceTotal ELSE 0 END) as total_spent,
  MAX(e.timestamp) as last_activity_date,
  MIN(e.timestamp) as first_activity_date
FROM profile_dataset p
LEFT JOIN experience_event_dataset e
  ON p.personalEmail.address = e.identityMap['email'][0].id
  AND e.timestamp >= CURRENT_DATE - INTERVAL '30' DAY
GROUP BY p.personalEmail.address, first_name, last_name, city, state;
```

### 18. Create Aggregated Metrics Table

```sql
-- Daily aggregated metrics for reporting
CREATE TABLE daily_commerce_metrics AS
SELECT
  DATE_TRUNC('day', timestamp) as metric_date,
  COUNT(DISTINCT identityMap['ECID'][0].id) as unique_visitors,
  COUNT(DISTINCT CASE WHEN eventType = 'commerce.productViews' THEN identityMap['ECID'][0].id END) as product_viewers,
  COUNT(DISTINCT CASE WHEN eventType = 'commerce.purchases' THEN identityMap['ECID'][0].id END) as purchasers,
  COUNT(CASE WHEN eventType = 'commerce.productViews' THEN 1 END) as total_product_views,
  COUNT(CASE WHEN eventType = 'commerce.productListAdds' THEN 1 END) as total_cart_adds,
  COUNT(CASE WHEN eventType = 'commerce.purchases' THEN 1 END) as total_purchases,
  SUM(CASE WHEN eventType = 'commerce.purchases' THEN commerce.order.priceTotal ELSE 0 END) as total_revenue
FROM experience_event_dataset
WHERE timestamp >= CURRENT_DATE - INTERVAL '90' DAY
GROUP BY metric_date
ORDER BY metric_date DESC;
```

## Query Optimization Tips

### 1. Use Partitioning

```sql
-- Filter by date to leverage partitioning
SELECT COUNT(*)
FROM experience_event_dataset
WHERE timestamp >= '2024-01-01'  -- Always include date filter
  AND timestamp < '2024-02-01';
```

### 2. Limit Result Sets

```sql
-- Always use LIMIT for exploratory queries
SELECT *
FROM profile_dataset
LIMIT 100;  -- Prevents accidentally reading entire dataset
```

### 3. Use EXISTS Instead of IN for Subqueries

```sql
-- More efficient with EXISTS
SELECT p.personalEmail.address
FROM profile_dataset p
WHERE EXISTS (
  SELECT 1
  FROM experience_event_dataset e
  WHERE e.identityMap['email'][0].id = p.personalEmail.address
    AND e.eventType = 'commerce.purchases'
    AND e.timestamp >= CURRENT_DATE - INTERVAL '30' DAY
);
```

### 4. Avoid SELECT *

```sql
-- Specify only needed columns
SELECT
  personalEmail.address,
  person.name.firstName,
  homeAddress.city
FROM profile_dataset
-- NOT: SELECT * FROM profile_dataset
```

## Query Service Functions

### Date/Time Functions

```sql
-- Current date/time
SELECT CURRENT_DATE, CURRENT_TIMESTAMP;

-- Date arithmetic
SELECT
  CURRENT_DATE - INTERVAL '7' DAY as week_ago,
  CURRENT_DATE + INTERVAL '1' MONTH as next_month;

-- Extract components
SELECT
  EXTRACT(YEAR FROM timestamp) as year,
  EXTRACT(MONTH FROM timestamp) as month,
  EXTRACT(DAY FROM timestamp) as day,
  EXTRACT(HOUR FROM timestamp) as hour;

-- Date truncation
SELECT
  DATE_TRUNC('day', timestamp) as day,
  DATE_TRUNC('week', timestamp) as week,
  DATE_TRUNC('month', timestamp) as month;
```

### String Functions

```sql
-- String manipulation
SELECT
  UPPER(person.name.firstName) as first_name_upper,
  LOWER(personalEmail.address) as email_lower,
  CONCAT(person.name.firstName, ' ', person.name.lastName) as full_name,
  SUBSTRING(personalEmail.address FROM 1 FOR POSITION('@' IN personalEmail.address) - 1) as email_username,
  REPLACE(mobilePhone.number, '-', '') as phone_digits_only;
```

### Aggregate Functions

```sql
-- Aggregations
SELECT
  COUNT(*) as total_count,
  COUNT(DISTINCT personalEmail.address) as unique_emails,
  SUM(commerce.order.priceTotal) as total_revenue,
  AVG(commerce.order.priceTotal) as avg_order_value,
  MIN(timestamp) as earliest_event,
  MAX(timestamp) as latest_event,
  STDDEV(commerce.order.priceTotal) as revenue_stddev;
```

## Additional Resources

- [Query Service SQL Reference](https://experienceleague.adobe.com/docs/experience-platform/query/sql/overview.html)
- [Query Service UI Guide](https://experienceleague.adobe.com/docs/experience-platform/query/ui/overview.html)
- [Scheduled Queries](https://experienceleague.adobe.com/docs/experience-platform/query/ui/query-schedules.html)
- [Query Service Best Practices](https://experienceleague.adobe.com/docs/experience-platform/query/best-practices/writing-queries.html)
