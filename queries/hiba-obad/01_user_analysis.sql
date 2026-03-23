-- ============================================
-- MEMBER 2: HIBA OBAD - USER ANALYSIS QUERIES
-- ============================================

-- Q1: Users joining each year
SELECT YEAR(yelping_since) as join_year, COUNT(*) as new_users
FROM users
GROUP BY YEAR(yelping_since)
ORDER BY join_year;

-- Q2: Top reviewers
SELECT name, review_count
FROM users
ORDER BY review_count DESC
LIMIT 20;

-- Q3: Most popular users by fans
SELECT name, fans
FROM users
ORDER BY fans DESC
LIMIT 20;

-- Q4: Elite users ratio each year
SELECT 
    YEAR(yelping_since) as join_year,
    COUNT(*) as total_users,
    SUM(CASE WHEN elite IS NOT NULL AND elite != '' THEN 1 ELSE 0 END) as elite_users,
    ROUND(SUM(CASE WHEN elite IS NOT NULL AND elite != '' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as elite_percentage
FROM users
GROUP BY YEAR(yelping_since)
ORDER BY join_year;

-- Q5: Silent users proportion
WITH user_reviews AS (
    SELECT user_id, COUNT(*) as review_count
    FROM review
    GROUP BY user_id
)
SELECT 
    YEAR(u.yelping_since) as join_year,
    COUNT(u.user_id) as total_users,
    SUM(CASE WHEN ur.user_id IS NULL THEN 1 ELSE 0 END) as silent_users,
    ROUND(SUM(CASE WHEN ur.user_id IS NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(u.user_id), 2) as silent_percentage
FROM users u
LEFT JOIN user_reviews ur ON u.user_id = ur.user_id
GROUP BY YEAR(u.yelping_since)
ORDER BY join_year;

-- Q6: Yearly statistics (new users, reviews, elite, tips, check-ins)
SELECT 
    COALESCE(u.year, r.year, t.year, c.year) as year,
    COALESCE(u.new_users, 0) as new_users,
    COALESCE(r.total_reviews, 0) as total_reviews,
    COALESCE(u.elite_users, 0) as elite_users,
    COALESCE(t.total_tips, 0) as total_tips,
    COALESCE(c.total_checkins, 0) as total_checkins
FROM (
    SELECT YEAR(yelping_since) as year, COUNT(*) as new_users,
           SUM(CASE WHEN elite IS NOT NULL AND elite != '' THEN 1 ELSE 0 END) as elite_users
    FROM users
    GROUP BY YEAR(yelping_since)
) u
FULL OUTER JOIN (
    SELECT YEAR(date) as year, COUNT(*) as total_reviews
    FROM review
    GROUP BY YEAR(date)
) r ON u.year = r.year
FULL OUTER JOIN (
    SELECT YEAR(date) as year, COUNT(*) as total_tips
    FROM tip
    GROUP BY YEAR(date)
) t ON u.year = t.year
FULL OUTER JOIN (
    SELECT YEAR(checkin_time) as year, COUNT(*) as total_checkins
    FROM (
        SELECT EXPLODE(SPLIT(date, ', ')) as checkin_time
        FROM checkin
    ) tmp
    GROUP BY YEAR(checkin_time)
) c ON u.year = c.year
ORDER BY year;
-- Q7: Early adopters (tastemakers)
WITH first_reviews AS (
    SELECT 
        r.business_id,
        r.user_id,
        ROW_NUMBER() OVER (PARTITION BY r.business_id ORDER BY r.date) as review_rank
    FROM review r
    JOIN business b ON r.business_id = b.business_id
    WHERE b.categories LIKE '%Restaurants%'
),
top_restaurants AS (
    SELECT business_id
    FROM business
    WHERE stars >= 4.5 AND review_count >= 100
)
SELECT u.user_id, u.name, COUNT(*) as early_reviews
FROM first_reviews fr
JOIN top_restaurants tr ON fr.business_id = tr.business_id
JOIN users u ON fr.user_id = u.user_id
WHERE fr.review_rank <= 5
GROUP BY u.user_id, u.name
ORDER BY early_reviews DESC
LIMIT 20;
