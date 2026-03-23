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

-- Q8: User rating evolution (first year vs third year)
WITH user_yearly_rating AS (
    SELECT 
        user_id,
        YEAR(date) as review_year,
        AVG(stars) as avg_rating
    FROM review
    GROUP BY user_id, YEAR(date)
),
user_join_year AS (
    SELECT user_id, YEAR(yelping_since) as join_year
    FROM users
)
SELECT 
    uj.user_id,
    uj.join_year,
    ROUND(yr1.avg_rating, 2) as first_year_rating,
    ROUND(yr3.avg_rating, 2) as third_year_rating,
    ROUND(yr3.avg_rating - yr1.avg_rating, 2) as rating_change
FROM user_join_year uj
LEFT JOIN user_yearly_rating yr1 ON uj.user_id = yr1.user_id AND yr1.review_year = uj.join_year
LEFT JOIN user_yearly_rating yr3 ON uj.user_id = yr3.user_id AND yr3.review_year = uj.join_year + 2
WHERE yr1.avg_rating IS NOT NULL AND yr3.avg_rating IS NOT NULL
ORDER BY rating_change;

-- Q9: Adventurous eaters (cuisine diversity)
SELECT 
    u.user_id,
    u.name,
    COUNT(DISTINCT cat.category) as cuisine_count,
    COUNT(r.review_id) as total_reviews
FROM users u
JOIN review r ON u.user_id = r.user_id
JOIN business b ON r.business_id = b.business_id
LATERAL VIEW EXPLODE(SPLIT(b.categories, ', ')) cat AS category
WHERE cat.category IN ('American', 'Mexican', 'Italian', 'Japanese', 'Chinese', 'Thai', 
                       'Mediterranean', 'French', 'Vietnamese', 'Greek', 'Indian', 'Korean',
                       'Hawaiian', 'African', 'Spanish', 'Middle Eastern')
GROUP BY u.user_id, u.name
HAVING total_reviews >= 20
ORDER BY cuisine_count DESC
LIMIT 50;

-- Q10: Elite status impact (review length & votes before/after)
WITH elite_users AS (
    SELECT 
        user_id,
        CAST(SPLIT(elite, ',')[0] AS INT) as first_elite_year
    FROM users
    WHERE elite IS NOT NULL AND elite != ''
),
reviews_with_status AS (
    SELECT 
        r.user_id,
        YEAR(r.date) as review_year,
        LENGTH(r.text) as review_length,
        (r.useful + r.funny + r.cool) as total_votes
    FROM review r
)
SELECT 
    eu.user_id,
    ROUND(AVG(CASE WHEN rws.review_year < eu.first_elite_year THEN rws.review_length END), 2) as avg_length_before,
    ROUND(AVG(CASE WHEN rws.review_year >= eu.first_elite_year THEN rws.review_length END), 2) as avg_length_after,
    ROUND(AVG(CASE WHEN rws.review_year < eu.first_elite_year THEN rws.total_votes END), 2) as avg_votes_before,
    ROUND(AVG(CASE WHEN rws.review_year >= eu.first_elite_year THEN rws.total_votes END), 2) as avg_votes_after
FROM elite_users eu
JOIN reviews_with_status rws ON eu.user_id = rws.user_id
GROUP BY eu.user_id
LIMIT 100;

-- Q11: Top 5 merchants per city (combined metrics)
WITH business_scores AS (
    SELECT 
        b.business_id,
        b.name,
        b.city,
        b.stars,
        b.review_count,
        COALESCE(cc.checkin_count, 0) as checkin_count,
        (b.stars / 5.0) * 0.4 + 
        (b.review_count / (SELECT MAX(review_count) FROM business)) * 0.3 +
        (COALESCE(cc.checkin_count, 0) / (SELECT MAX(COALESCE(checkin_count, 0)) 
            FROM (SELECT business_id, COUNT(*) as checkin_count FROM checkin GROUP BY business_id) t)) * 0.3 as combined_score
    FROM business b
    LEFT JOIN (
        SELECT business_id, COUNT(*) as checkin_count
        FROM checkin
        GROUP BY business_id
    ) cc ON b.business_id = cc.business_id
    WHERE b.city IS NOT NULL
),
ranked AS (
    SELECT 
        city,
        name,
        stars,
        review_count,
        checkin_count,
        ROUND(combined_score, 4) as score,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY combined_score DESC) as rank
    FROM business_scores
)
SELECT city, name, stars, review_count, checkin_count, score
FROM ranked
WHERE rank <= 5
ORDER BY city, rank
LIMIT 100;

-- Q12: Review conversion rate (check-ins / reviews)
SELECT 
    b.name,
    b.city,
    b.review_count,
    COALESCE(cc.checkin_count, 0) as checkin_count,
    ROUND(COALESCE(cc.checkin_count, 0) * 1.0 / b.review_count, 4) as conversion_rate
FROM business b
LEFT JOIN (
    SELECT business_id, COUNT(*) as checkin_count
    FROM checkin
    GROUP BY business_id
) cc ON b.business_id = cc.business_id
WHERE b.review_count > 0
ORDER BY conversion_rate DESC
LIMIT 100;

-- Q13: Post-review check-in drop-off
WITH review_spikes AS (
    SELECT 
        business_id,
        DATE_FORMAT(date, 'yyyy-MM') as spike_month,
        COUNT(*) as bad_review_count,
        AVG(stars) as avg_rating
    FROM review
    GROUP BY business_id, DATE_FORMAT(date, 'yyyy-MM')
    HAVING AVG(stars) <= 2 AND COUNT(*) >= 5
),
checkin_trend AS (
    SELECT 
        c.business_id,
        DATE_FORMAT(checkin_time, 'yyyy-MM') as checkin_month,
        COUNT(*) as checkin_count
    FROM (
        SELECT business_id, EXPLODE(SPLIT(date, ', ')) as checkin_time
        FROM checkin
    ) c
    GROUP BY c.business_id, DATE_FORMAT(checkin_time, 'yyyy-MM')
),
dropoff_calc AS (
    SELECT 
        rs.business_id,
        b.name,
        rs.spike_month,
        rs.bad_review_count,
        ct.checkin_count as checkins_during_spike,
        LEAD(ct.checkin_count, 1) OVER (PARTITION BY rs.business_id ORDER BY ct.checkin_month) as next_month_checkins,
        ROUND((LEAD(ct.checkin_count, 1) OVER (PARTITION BY rs.business_id ORDER BY ct.checkin_month) - ct.checkin_count) * 100.0 / ct.checkin_count, 2) as dropoff_percentage
    FROM review_spikes rs
    JOIN business b ON rs.business_id = b.business_id
    LEFT JOIN checkin_trend ct ON rs.business_id = ct.business_id AND rs.spike_month = ct.checkin_month
    WHERE ct.checkin_count > 0
)
SELECT business_id, name, spike_month, bad_review_count, checkins_during_spike, next_month_checkins, dropoff_percentage
FROM dropoff_calc
WHERE dropoff_percentage IS NOT NULL
ORDER BY ABS(dropoff_percentage) DESC
LIMIT 50;

-- Q8: User rating evolution (first year vs third year)
WITH user_yearly_rating AS (
    SELECT 
        user_id,
        YEAR(date) as review_year,
        AVG(stars) as avg_rating
    FROM review
    GROUP BY user_id, YEAR(date)
),
user_join_year AS (
    SELECT user_id, YEAR(yelping_since) as join_year
    FROM users
)
SELECT 
    uj.user_id,
    uj.join_year,
    ROUND(yr1.avg_rating, 2) as first_year_rating,
    ROUND(yr3.avg_rating, 2) as third_year_rating,
    ROUND(yr3.avg_rating - yr1.avg_rating, 2) as rating_change
FROM user_join_year uj
LEFT JOIN user_yearly_rating yr1 ON uj.user_id = yr1.user_id AND yr1.review_year = uj.join_year
LEFT JOIN user_yearly_rating yr3 ON uj.user_id = yr3.user_id AND yr3.review_year = uj.join_year + 2
WHERE yr1.avg_rating IS NOT NULL AND yr3.avg_rating IS NOT NULL
ORDER BY rating_change;

-- Q9: Adventurous eaters (cuisine diversity)
SELECT 
    u.user_id,
    u.name,
    COUNT(DISTINCT cat.category) as cuisine_count,
    COUNT(r.review_id) as total_reviews
FROM users u
JOIN review r ON u.user_id = r.user_id
JOIN business b ON r.business_id = b.business_id
LATERAL VIEW EXPLODE(SPLIT(b.categories, ', ')) cat AS category
WHERE cat.category IN ('American', 'Mexican', 'Italian', 'Japanese', 'Chinese', 'Thai', 
                       'Mediterranean', 'French', 'Vietnamese', 'Greek', 'Indian', 'Korean',
                       'Hawaiian', 'African', 'Spanish', 'Middle Eastern')
GROUP BY u.user_id, u.name
HAVING total_reviews >= 20
ORDER BY cuisine_count DESC
LIMIT 50;

-- Q10: Elite status impact (review length & votes before/after)
WITH elite_users AS (
    SELECT 
        user_id,
        CAST(SPLIT(elite, ',')[0] AS INT) as first_elite_year
    FROM users
    WHERE elite IS NOT NULL AND elite != ''
),
reviews_with_status AS (
    SELECT 
        r.user_id,
        YEAR(r.date) as review_year,
        LENGTH(r.text) as review_length,
        (r.useful + r.funny + r.cool) as total_votes
    FROM review r
)
SELECT 
    eu.user_id,
    ROUND(AVG(CASE WHEN rws.review_year < eu.first_elite_year THEN rws.review_length END), 2) as avg_length_before,
    ROUND(AVG(CASE WHEN rws.review_year >= eu.first_elite_year THEN rws.review_length END), 2) as avg_length_after,
    ROUND(AVG(CASE WHEN rws.review_year < eu.first_elite_year THEN rws.total_votes END), 2) as avg_votes_before,
    ROUND(AVG(CASE WHEN rws.review_year >= eu.first_elite_year THEN rws.total_votes END), 2) as avg_votes_after
FROM elite_users eu
JOIN reviews_with_status rws ON eu.user_id = rws.user_id
GROUP BY eu.user_id
LIMIT 100;

-- Q11: Top 5 merchants per city (combined metrics)
WITH business_scores AS (
    SELECT 
        b.business_id,
        b.name,
        b.city,
        b.stars,
        b.review_count,
        COALESCE(cc.checkin_count, 0) as checkin_count,
        (b.stars / 5.0) * 0.4 + 
        (b.review_count / (SELECT MAX(review_count) FROM business)) * 0.3 +
        (COALESCE(cc.checkin_count, 0) / (SELECT MAX(COALESCE(checkin_count, 0)) 
            FROM (SELECT business_id, COUNT(*) as checkin_count FROM checkin GROUP BY business_id) t)) * 0.3 as combined_score
    FROM business b
    LEFT JOIN (
        SELECT business_id, COUNT(*) as checkin_count
        FROM checkin
        GROUP BY business_id
    ) cc ON b.business_id = cc.business_id
    WHERE b.city IS NOT NULL
),
ranked AS (
    SELECT 
        city,
        name,
        stars,
        review_count,
        checkin_count,
        ROUND(combined_score, 4) as score,
        ROW_NUMBER() OVER (PARTITION BY city ORDER BY combined_score DESC) as rank
    FROM business_scores
)
SELECT city, name, stars, review_count, checkin_count, score
FROM ranked
WHERE rank <= 5
ORDER BY city, rank
LIMIT 100;

-- Q12: Review conversion rate (check-ins / reviews)
SELECT 
    b.name,
    b.city,
    b.review_count,
    COALESCE(cc.checkin_count, 0) as checkin_count,
    ROUND(COALESCE(cc.checkin_count, 0) * 1.0 / b.review_count, 4) as conversion_rate
FROM business b
LEFT JOIN (
    SELECT business_id, COUNT(*) as checkin_count
    FROM checkin
    GROUP BY business_id
) cc ON b.business_id = cc.business_id
WHERE b.review_count > 0
ORDER BY conversion_rate DESC
LIMIT 100;

-- Q13: Post-review check-in drop-off
WITH review_spikes AS (
    SELECT 
        business_id,
        DATE_FORMAT(date, 'yyyy-MM') as spike_month,
        COUNT(*) as bad_review_count,
        AVG(stars) as avg_rating
    FROM review
    GROUP BY business_id, DATE_FORMAT(date, 'yyyy-MM')
    HAVING AVG(stars) <= 2 AND COUNT(*) >= 5
),
checkin_trend AS (
    SELECT 
        c.business_id,
        DATE_FORMAT(checkin_time, 'yyyy-MM') as checkin_month,
        COUNT(*) as checkin_count
    FROM (
        SELECT business_id, EXPLODE(SPLIT(date, ', ')) as checkin_time
        FROM checkin
    ) c
    GROUP BY c.business_id, DATE_FORMAT(checkin_time, 'yyyy-MM')
),
dropoff_calc AS (
    SELECT 
        rs.business_id,
        b.name,
        rs.spike_month,
        rs.bad_review_count,
        ct.checkin_count as checkins_during_spike,
        LEAD(ct.checkin_count, 1) OVER (PARTITION BY rs.business_id ORDER BY ct.checkin_month) as next_month_checkins,
        ROUND((LEAD(ct.checkin_count, 1) OVER (PARTITION BY rs.business_id ORDER BY ct.checkin_month) - ct.checkin_count) * 100.0 / ct.checkin_count, 2) as dropoff_percentage
    FROM review_spikes rs
    JOIN business b ON rs.business_id = b.business_id
    LEFT JOIN checkin_trend ct ON rs.business_id = ct.business_id AND rs.spike_month = ct.checkin_month
    WHERE ct.checkin_count > 0
)
SELECT business_id, name, spike_month, bad_review_count, checkins_during_spike, next_month_checkins, dropoff_percentage
FROM dropoff_calc
WHERE dropoff_percentage IS NOT NULL
ORDER BY ABS(dropoff_percentage) DESC
LIMIT 50;
