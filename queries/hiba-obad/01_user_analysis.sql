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
