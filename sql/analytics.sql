-- ============================================================
-- DIGITAL PAYMENTS & BEHAVIORAL INTELLIGENCE PLATFORM
-- SQL ANALYTICS
-- DuckDB
-- ============================================================


-- ============================================================
-- 1. EXECUTIVE TRANSACTION KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_usd), 2) AS total_transaction_volume,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value,
    ROUND(MEDIAN(amount_usd), 2) AS median_transaction_value,
    ROUND(MIN(amount_usd), 2) AS minimum_transaction_value,
    ROUND(MAX(amount_usd), 2) AS maximum_transaction_value
FROM 'data/processed_transactions.parquet';


-- ============================================================
-- 2. TRANSACTION PERFORMANCE BY MERCHANT CATEGORY
-- ============================================================

SELECT
    merchant_category,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_usd), 2) AS total_transaction_volume,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value,
    ROUND(MEDIAN(amount_usd), 2) AS median_transaction_value
FROM 'data/processed_transactions.parquet'
GROUP BY merchant_category
ORDER BY total_transaction_volume DESC;


-- ============================================================
-- 3. TRANSACTION PERFORMANCE BY CHANNEL
-- ============================================================

SELECT
    channel,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_usd), 2) AS total_transaction_volume,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value
FROM 'data/processed_transactions.parquet'
GROUP BY channel
ORDER BY total_transaction_volume DESC;


-- ============================================================
-- 4. AUTHENTICATION METHOD ANALYSIS
-- ============================================================

SELECT
    auth_method,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_usd), 2) AS total_transaction_volume,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share_percent
FROM 'data/processed_transactions.parquet'
GROUP BY auth_method
ORDER BY transaction_count DESC;


-- ============================================================
-- 5. TRANSACTION ACTIVITY BY TIME OF DAY
-- ============================================================

SELECT
    time_of_day_period,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_usd), 2) AS total_transaction_volume,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value
FROM 'data/processed_transactions.parquet'
GROUP BY time_of_day_period
ORDER BY total_transaction_volume DESC;


-- ============================================================
-- 6. RISK INDICATOR ANALYSIS
-- ============================================================

SELECT
    composite_risk_flags,
    COUNT(*) AS transaction_count,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value,
    ROUND(
        100.0 * COUNT(*) /
        SUM(COUNT(*)) OVER (),
        2
    ) AS transaction_share_percent
FROM 'data/processed_transactions.parquet'
GROUP BY composite_risk_flags
ORDER BY composite_risk_flags DESC;


-- ============================================================
-- 7. FRAUD RATE BY RISK LEVEL
-- ============================================================

SELECT
    risk_level,
    COUNT(*) AS transaction_count,
    SUM(is_fraud) AS fraudulent_transactions,
    ROUND(
        100.0 * SUM(is_fraud) / COUNT(*),
        2
    ) AS fraud_rate_percent,
    ROUND(AVG(anomaly_score), 4) AS average_anomaly_score
FROM 'data/processed_transactions.parquet'
GROUP BY risk_level
ORDER BY fraud_rate_percent DESC;


-- ============================================================
-- 8. BEHAVIORAL SEGMENT ANALYSIS
-- ============================================================

SELECT
    behavior_segment,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_usd), 2) AS total_transaction_volume,
    ROUND(AVG(amount_usd), 2) AS average_transaction_value,
    ROUND(AVG(velocity_score), 2) AS average_velocity_score,
    ROUND(AVG(distance_from_home_km), 2) AS average_distance_from_home,
    ROUND(AVG(merchant_risk_score), 2) AS average_merchant_risk,
    ROUND(
        100.0 * SUM(is_fraud) / COUNT(*),
        2
    ) AS fraud_rate_percent
FROM 'data/processed_transactions.parquet'
GROUP BY behavior_segment
ORDER BY behavior_segment;


-- ============================================================
-- 9. HIGH-VALUE TRANSACTIONS WITH RISK SIGNALS
-- ============================================================

WITH transaction_threshold AS (

    SELECT
        QUANTILE_CONT(amount_usd, 0.90) AS high_value_threshold
    FROM 'data/processed_transactions.parquet'

)

SELECT
    t.transaction_id,
    t.amount_usd,
    t.merchant_category,
    t.channel,
    t.auth_method,
    t.velocity_score,
    t.composite_risk_flags,
    t.anomaly_score,
    t.risk_level,
    t.is_fraud

FROM 'data/processed_transactions.parquet' AS t

CROSS JOIN transaction_threshold AS threshold

WHERE
    t.amount_usd >= threshold.high_value_threshold
    AND t.risk_level = 'Elevated'

ORDER BY
    t.amount_usd DESC;


-- ============================================================
-- 10. RANK MERCHANT CATEGORIES BY TRANSACTION VALUE
-- Demonstrates a SQL window function
-- ============================================================

WITH category_performance AS (

    SELECT
        merchant_category,
        COUNT(*) AS transaction_count,
        SUM(amount_usd) AS total_transaction_volume
    FROM 'data/processed_transactions.parquet'
    GROUP BY merchant_category

)

SELECT
    merchant_category,
    transaction_count,
    ROUND(total_transaction_volume, 2)
        AS total_transaction_volume,

    RANK() OVER (
        ORDER BY total_transaction_volume DESC
    ) AS volume_rank

FROM category_performance

ORDER BY volume_rank;


-- ============================================================
-- 11. CHANNEL RISK ANALYSIS
-- ============================================================

SELECT
    channel,
    COUNT(*) AS transaction_count,

    SUM(is_fraud) AS fraudulent_transactions,

    ROUND(
        100.0 * SUM(is_fraud) / COUNT(*),
        2
    ) AS fraud_rate_percent,

    ROUND(
        AVG(composite_risk_flags),
        2
    ) AS average_risk_flags,

    ROUND(
        AVG(anomaly_score),
        4
    ) AS average_anomaly_score

FROM 'data/processed_transactions.parquet'

GROUP BY channel

ORDER BY fraud_rate_percent DESC;


-- ============================================================
-- 12. TRANSACTIONS WITH MULTIPLE RISK INDICATORS
-- ============================================================

-- 12
SELECT
    transaction_id,
    amount_usd,
    merchant_category,
    channel,
    auth_method,
    used_vpn,
    ip_country_mismatch,
    billing_shipping_mismatch,
    is_ai_generated_scam_attempt,
    composite_risk_flags,
    anomaly_flag,
    anomaly_score,
    risk_level,
    is_fraud
FROM 'data/processed_transactions.parquet'
WHERE composite_risk_flags >= 2
ORDER BY
    composite_risk_flags DESC,
    anomaly_flag DESC,
    anomaly_score DESC
LIMIT 50;