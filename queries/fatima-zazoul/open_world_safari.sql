-- Open World Safari - External Data Enrichment
-- Combines Yelp data with US Census Bureau data

SELECT 
    b.city,
    b.postal_code,
    census.median_income,
    COUNT(DISTINCT b.business_id) as total_businesses,
    AVG(r.stars) as avg_rating
FROM business b
LEFT JOIN review r ON b.business_id = r.business_id
LEFT JOIN census_data c ON b.postal_code = c.zip_code
GROUP BY b.city, b.postal_code, census.median_income
ORDER BY census.median_income DESC;
