-- Healthcare Billing Data Analysis SQL Queries
-- These queries demonstrate SQL skills for data extraction and transformation

-- 1. BASIC DATA EXPLORATION
-- ========================================

-- Overview of the dataset
SELECT 
    COUNT(*) as total_claims,
    COUNT(DISTINCT patient_id) as unique_patients,
    COUNT(DISTINCT provider_id) as unique_providers,
    COUNT(DISTINCT insurance_provider) as unique_insurers,
    MIN(service_date) as earliest_service,
    MAX(service_date) as latest_service,
    SUM(total_billed_amount) as total_revenue,
    AVG(total_billed_amount) as avg_claim_amount
FROM healthcare_billing_main;

-- 2. COST ANALYSIS BY PROCEDURE
-- ========================================

-- Top procedures by revenue and volume
SELECT 
    procedure_name,
    procedure_complexity,
    COUNT(*) as claim_count,
    SUM(total_billed_amount) as total_revenue,
    AVG(total_billed_amount) as avg_cost,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_billed_amount) as median_cost,
    STDDEV(total_billed_amount) as cost_std_dev,
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_rate_pct
FROM healthcare_billing_main
GROUP BY procedure_name, procedure_complexity
ORDER BY total_revenue DESC;

-- 3. PROVIDER PERFORMANCE ANALYSIS
-- ========================================

-- Provider performance metrics with risk assessment
WITH provider_metrics AS (
    SELECT 
        provider_id,
        COUNT(*) as total_claims,
        COUNT(DISTINCT patient_id) as unique_patients,
        SUM(total_billed_amount) as total_revenue,
        AVG(total_billed_amount) as avg_claim_amount,
        SUM(insurance_paid_amount) as total_insurance_paid,
        AVG(payment_rate) as avg_payment_rate,
        SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
        AVG(length_of_stay) as avg_length_stay
    FROM healthcare_billing_main
    GROUP BY provider_id
),
provider_risk AS (
    SELECT *,
        ROUND((anomaly_count * 100.0 / total_claims), 2) as anomaly_rate_pct,
        ROUND((total_revenue / unique_patients), 2) as revenue_per_patient,
        CASE 
            WHEN (anomaly_count * 100.0 / total_claims) > 10 THEN 'High Risk'
            WHEN (anomaly_count * 100.0 / total_claims) > 5 THEN 'Medium Risk'
            ELSE 'Low Risk'
        END as risk_category
    FROM provider_metrics
    WHERE total_claims >= 10  -- Filter for providers with meaningful volume
)
SELECT *
FROM provider_risk
ORDER BY anomaly_rate_pct DESC, total_revenue DESC;

-- 4. TEMPORAL ANALYSIS
-- ========================================

-- Monthly trends with year-over-year comparison
WITH monthly_stats AS (
    SELECT 
        service_year,
        EXTRACT(MONTH FROM CAST(service_date AS DATE)) as service_month,
        COUNT(*) as monthly_claims,
        SUM(total_billed_amount) as monthly_revenue,
        AVG(total_billed_amount) as avg_claim_amount,
        SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as monthly_anomalies,
        COUNT(DISTINCT patient_id) as unique_patients
    FROM healthcare_billing_main
    GROUP BY service_year, EXTRACT(MONTH FROM CAST(service_date AS DATE))
)
SELECT 
    service_year,
    service_month,
    monthly_claims,
    monthly_revenue,
    avg_claim_amount,
    monthly_anomalies,
    ROUND((monthly_anomalies * 100.0 / monthly_claims), 2) as anomaly_rate_pct,
    unique_patients,
    LAG(monthly_revenue, 12) OVER (ORDER BY service_year, service_month) as same_month_prev_year,
    ROUND(((monthly_revenue - LAG(monthly_revenue, 12) OVER (ORDER BY service_year, service_month)) 
           / LAG(monthly_revenue, 12) OVER (ORDER BY service_year, service_month) * 100), 2) as yoy_growth_pct
FROM monthly_stats
ORDER BY service_year, service_month;

-- 5. INSURANCE ANALYSIS
-- ========================================

-- Insurance provider efficiency and patterns
SELECT 
    insurance_provider,
    COUNT(*) as total_claims,
    COUNT(DISTINCT patient_id) as unique_patients,
    SUM(total_billed_amount) as total_billed,
    SUM(insurance_paid_amount) as total_paid,
    AVG(payment_rate) as avg_payment_rate,
    ROUND(SUM(insurance_paid_amount) / SUM(total_billed_amount) * 100, 2) as overall_payment_rate_pct,
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_rate_pct,
    AVG(length_of_stay) as avg_length_stay
FROM healthcare_billing_main
GROUP BY insurance_provider
ORDER BY total_billed DESC;

-- 6. ANOMALY DETECTION ANALYSIS
-- ========================================

-- Detailed anomaly analysis by multiple dimensions
WITH anomaly_analysis AS (
    SELECT 
        CASE WHEN final_anomaly_flag = 1 THEN 'Anomalous' ELSE 'Normal' END as anomaly_status,
        procedure_name,
        age_group,
        insurance_provider,
        department,
        COUNT(*) as claim_count,
        AVG(total_billed_amount) as avg_cost,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_billed_amount) as median_cost,
        MAX(total_billed_amount) as max_cost,
        AVG(length_of_stay) as avg_length_stay
    FROM healthcare_billing_main
    GROUP BY 
        CASE WHEN final_anomaly_flag = 1 THEN 'Anomalous' ELSE 'Normal' END,
        procedure_name, age_group, insurance_provider, department
)
SELECT *
FROM anomaly_analysis
WHERE anomaly_status = 'Anomalous'
ORDER BY avg_cost DESC;

-- 7. HIGH-VALUE CLAIMS ANALYSIS
-- ========================================

-- Analysis of high-value claims (top 5% by cost)
WITH high_value_threshold AS (
    SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_billed_amount) as threshold_95
    FROM healthcare_billing_main
),
high_value_claims AS (
    SELECT h.*, t.threshold_95
    FROM healthcare_billing_main h
    CROSS JOIN high_value_threshold t
    WHERE h.total_billed_amount >= t.threshold_95
)
SELECT 
    procedure_name,
    department,
    COUNT(*) as high_value_count,
    AVG(total_billed_amount) as avg_high_value_cost,
    MAX(total_billed_amount) as max_cost,
    SUM(total_billed_amount) as total_high_value_revenue,
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_rate_pct
FROM high_value_claims
GROUP BY procedure_name, department
ORDER BY total_high_value_revenue DESC;

-- 8. PATIENT DEMOGRAPHICS AND COST PATTERNS
-- ========================================

-- Cost analysis by patient demographics
SELECT 
    age_group,
    patient_gender,
    COUNT(*) as claim_count,
    COUNT(DISTINCT patient_id) as unique_patients,
    AVG(total_billed_amount) as avg_cost_per_claim,
    SUM(total_billed_amount) / COUNT(DISTINCT patient_id) as avg_cost_per_patient,
    AVG(insurance_paid_amount) as avg_insurance_payment,
    AVG(patient_responsibility) as avg_patient_responsibility,
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_rate_pct
FROM healthcare_billing_main
GROUP BY age_group, patient_gender
ORDER BY avg_cost_per_claim DESC;

-- 9. DUPLICATE CLAIMS INVESTIGATION
-- ========================================

-- Identify potential duplicate claims for fraud detection
WITH potential_duplicates AS (
    SELECT 
        patient_id,
        provider_id,
        procedure_name,
        service_date,
        COUNT(*) as duplicate_count,
        SUM(total_billed_amount) as total_duplicate_amount,
        STRING_AGG(claim_id, ', ') as claim_ids
    FROM healthcare_billing_main
    GROUP BY patient_id, provider_id, procedure_name, service_date
    HAVING COUNT(*) > 1
)
SELECT 
    *,
    ROUND(total_duplicate_amount / duplicate_count, 2) as avg_duplicate_amount
FROM potential_duplicates
ORDER BY total_duplicate_amount DESC;

-- 10. DEPARTMENT EFFICIENCY ANALYSIS
-- ========================================

-- Department performance and efficiency metrics
SELECT 
    department,
    COUNT(*) as total_claims,
    COUNT(DISTINCT provider_id) as unique_providers,
    COUNT(DISTINCT patient_id) as unique_patients,
    SUM(total_billed_amount) as total_revenue,
    AVG(total_billed_amount) as avg_claim_amount,
    AVG(length_of_stay) as avg_length_stay,
    AVG(payment_rate) as avg_payment_rate,
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_rate_pct,
    ROUND(SUM(total_billed_amount) / COUNT(DISTINCT provider_id), 2) as revenue_per_provider
FROM healthcare_billing_main
GROUP BY department
ORDER BY total_revenue DESC;

-- 11. SEASONAL PATTERNS ANALYSIS
-- ========================================

-- Identify seasonal patterns in healthcare billing
SELECT 
    EXTRACT(MONTH FROM CAST(service_date AS DATE)) as month,
    CASE 
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (6, 7, 8) THEN 'Summer'
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (9, 10, 11) THEN 'Fall'
    END as season,
    COUNT(*) as claim_count,
    SUM(total_billed_amount) as total_revenue,
    AVG(total_billed_amount) as avg_claim_amount,
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END) as anomaly_count,
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as anomaly_rate_pct
FROM healthcare_billing_main
GROUP BY 
    EXTRACT(MONTH FROM CAST(service_date AS DATE)),
    CASE 
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (6, 7, 8) THEN 'Summer'
        WHEN EXTRACT(MONTH FROM CAST(service_date AS DATE)) IN (9, 10, 11) THEN 'Fall'
    END
ORDER BY month;

-- 12. COMPREHENSIVE KPI DASHBOARD QUERY
-- ========================================

-- Single query for key performance indicators
SELECT 
    'Total Claims' as kpi_name,
    COUNT(*)::text as kpi_value
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Total Revenue',
    '$' || ROUND(SUM(total_billed_amount)::numeric, 0)::text
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Average Claim Amount',
    '$' || ROUND(AVG(total_billed_amount)::numeric, 2)::text
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Total Anomalies',
    SUM(CASE WHEN final_anomaly_flag = 1 THEN 1 ELSE 0 END)::text
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Anomaly Rate (%)',
    ROUND(AVG(CASE WHEN final_anomaly_flag = 1 THEN 1.0 ELSE 0.0 END) * 100, 2)::text
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Unique Patients',
    COUNT(DISTINCT patient_id)::text
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Unique Providers',
    COUNT(DISTINCT provider_id)::text
FROM healthcare_billing_main

UNION ALL

SELECT 
    'Average Length of Stay',
    ROUND(AVG(length_of_stay)::numeric, 1)::text || ' days'
FROM healthcare_billing_main;
