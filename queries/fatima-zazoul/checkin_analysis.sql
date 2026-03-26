-- ============================================
-- CHECK-IN ANALYSIS - YELP DATASET
-- Extracted from checkin_analysis_notebook.zpln
-- ============================================

-- 1. Most popular city for check-ins
SELECT b.city, COUNT(*) as checkin_count
FROM checkin c
JOIN business b ON c.business_id = b.business_id
GROUP BY b.city
ORDER BY checkin_count DESC
LIMIT 10;

-- 2. Rank businesses by check-in counts
SELECT b.name, b.city, COUNT(*) as checkin_count
FROM checkin c
JOIN business b ON c.business_id = b.business_id
GROUP BY b.name, b.city
ORDER BY checkin_count DESC
LIMIT 50;

-- 3. Seasonality analysis - Ice Cream vs Soup
SELECT 
    CASE 
        WHEN b.categories LIKE '%Ice Cream%' THEN 'Ice Cream'
        WHEN b.categories LIKE '%Soup%' THEN 'Soup'
    END as cuisine_type,
    MONTH(r.review_date) as month,
    COUNT(*) as review_count
FROM review r
JOIN business b ON r.business_id = b.business_id
WHERE (b.categories LIKE '%Ice Cream%' OR b.categories LIKE '%Soup%')
GROUP BY 
    CASE WHEN b.categories LIKE '%Ice Cream%' THEN 'Ice Cream' ELSE 'Soup' END,
    MONTH(r.review_date)
ORDER BY cuisine_type, month;
