-- Rating Distribution
SELECT stars, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM review), 2) as percentage
FROM review
GROUP BY stars
ORDER BY stars;

-- Weekly Rating Frequency
SELECT 
    CASE DAYOFWEEK(review_date)
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END as day_of_week,
    COUNT(*) as review_count,
    AVG(stars) as avg_rating
FROM review
WHERE review_date IS NOT NULL
GROUP BY DAYOFWEEK(review_date)
ORDER BY DAYOFWEEK(review_date);

-- Top Businesses with Most 5-Star Reviews
SELECT b.name, COUNT(*) as five_star_count
FROM review r
JOIN business b ON r.business_id = b.business_id
WHERE r.stars = 5
GROUP BY b.name
ORDER BY five_star_count DESC
LIMIT 20;

-- Top 10 Cities with Highest Ratings
SELECT b.city, 
       COUNT(*) as review_count,
       AVG(r.stars) as avg_rating
FROM review r
JOIN business b ON r.business_id = b.business_id
GROUP BY b.city
HAVING COUNT(*) >= 100
ORDER BY avg_rating DESC
LIMIT 10;

-- Weekend vs Weekday for Nightlife
SELECT 
    CASE 
        WHEN DAYOFWEEK(r.review_date) IN (1, 7) THEN 'Weekend'
        ELSE 'Weekday'
    END as day_type,
    COUNT(*) as review_count,
    AVG(r.stars) as avg_rating
FROM review r
JOIN business b ON r.business_id = b.business_id
WHERE b.categories LIKE '%Nightlife%'
GROUP BY day_type;
