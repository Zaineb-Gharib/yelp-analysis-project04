The Review Manipulation Syndicate: How Ghost Accounts Kill Trust
Author: Hajar Choukri
Date: March 28, 2026
Project: Yelp Big Data Analysis – Requirement 2

Executive Summary
This report investigates businesses hiring "ghost accounts" to flood their pages with 5-star reviews. Using the Yelp dataset, we analyzed reviews to understand how manipulation works and whether it pays off.

Our findings reveal clear patterns. Manipulated businesses show extreme five-star ratios from users who review the same few businesses repeatedly with no rating variance. The long-term consequences are significant—businesses that manipulate experience rating drops after suspicious activity peaks.

External validation on Yelp's website confirmed ghost accounts: new profiles with exactly one review, created days before posting a 5-star rating, with no photos or friends. These businesses showed clustered outbreaks—multiple 5-star reviews in short periods after months of silence. Recent 1-star complaints from real customers confirmed the deception.

Methodology
1. Data Preparation
I loaded review data from HDFS using spark.read.option("delimiter", "\u0001").csv("/user/hive/warehouse/review/") and selected review_id, user_id, business_id, stars, useful, funny, cool, text, and date. I extracted year from date using substring(col("date"), 1, 4).cast("int") and filtered for 2000–2025. I also loaded business data with business_id, name, and categories.

2. Creating User Features
I grouped by user_id and calculated total_reviews, avg_rating, rating_stddev, five_star_count, one_star_count, and unique_businesses using countDistinct. I filtered to users with at least 5 reviews. I derived five_star_ratio, one_star_ratio, and business_clustering_ratio.

3. Creating Business Features
I grouped by business_id and calculated total_reviews, avg_rating, rating_stddev, and five_star_count. I filtered to businesses with at least 20 reviews and derived five_star_ratio.

4. Detecting Review Spikes
I grouped by business_id and date to get daily_reviews. Using a Window with rowsBetween(-6, 0), I calculated 7-day rolling averages and flagged spikes where daily_reviews > rolling_7d_avg * 3. I counted spike days per business.

5. Suspicious User Detection
I created suspicion_score by adding:

40 points if five_star_ratio > 0.9 OR one_star_ratio > 0.9

30 points if rating_stddev < 0.5

30 points if business_clustering_ratio < 0.2

I classified users as High Risk (>80), Medium Risk (50–80), Low Risk (30–50), or Normal (<30). I detected review bursts (5+ reviews/day) and removed these users from the suspicious pool.

6. Business Manipulation Detection
I calculated suspicious_ratio for each business by counting reviews from suspicious users divided by total reviews. I joined with business_features and business_spikes, filled null spikes with 0, and created manipulation_score:

suspicious_ratio * 40

five_star_ratio * 30

30 if spike_count > 0

I classified businesses as Critical Risk (>80), High Risk (60–80), Medium Risk (40–60), or Low Risk (<40).

7. Network Analysis & Farm Detection
I collected suspicious user IDs (score >50, limited to 1000) and suspicious business IDs (score >40, limited to 50). I filtered reviews where both conditions matched, grouped by business_id, collected user sets with collect_set, and counted suspicious users per business. I filtered for businesses with at least 2 suspicious users and ordered by farm size.

8. Long-Term Impact Analysis
I took the top 50 suspicious businesses (score >40). I extracted month from date using date_format("date", "yyyy-MM"), grouped by business_id and month, and calculated avg_rating per month. For each business, I calculated rating drop (peak rating minus lowest rating) and months analyzed.

9. External Validation
I joined suspicious businesses with business data to get names. I selected the top 15 suspicious businesses by manipulation_score and manually searched them on Yelp. I examined reviewer profiles for ghost accounts (1 total review, newly created, no photo, no friends), looked for clustered outbreaks (multiple 5-star reviews in short windows), and checked for recent 1-star complaints.

Key Findings
Suspicious Users: I flagged thousands of users with high-risk scores. These users gave extreme five-star ratings to the same few businesses.

Manipulated Businesses: I flagged over a thousand businesses, with hundreds at Critical Risk. These showed extreme five-star ratios and review spikes.

Ghost Accounts: On Yelp, I found businesses where every 5-star reviewer had exactly one total review, accounts created within the same week, no profile photos, and no friends.

Clustered Outbreaks: After months of silence, businesses received many 5-star reviews in days, then silence again—a clear coordinated pattern.

Manipulation Backfires: Businesses that manipulated experienced significant rating drops from their peak as real customers discovered the deception.

Real Customers Complained: Recent 1-star reviews said things like "I was tricked by the fake reviews" and "Completely misleading ratings."

Critical Insights
Ghost Accounts Are the Tool: Fake reviews come from newly created accounts that post once and disappear.

Clustered Outbreaks Are the Signature: Silence, then a burst of 5-star reviews, then silence again—this is not organic.

Manipulation Always Backfires: Short-term rating boosts lead to long-term declines as real customers expose the deception.

Real Customers Notice: Angry 1-star reviews explicitly mention fake reviews and warn others.    Recommendations
For Platforms: Detect ghost accounts by flagging new accounts with one review, no photos, and no friends. Build automated spike detection for businesses receiving multiple 5-star reviews in short windows. Rank suspicious reviews lower.

For Investors: Avoid businesses with clustered 5-star outbreaks, reviews from one-review accounts, or recent complaints about fake reviews.

For Consumers: Check reviewer profiles. If a business has many 5-star reviews but every reviewer has only one review, something is wrong. Believe recent 1-star complaints about deception.

Conclusion
The review manipulation syndicate is real. Ghost accounts posting clustered 5-star outbreaks are the mechanism. Businesses that cheat see short-term rating boosts followed by long-term declines as real customers expose the deception.

The solution is straightforward. Detect ghost accounts. Flag clustered outbreaks. Remove fake reviews. Invest in honest businesses.

MANIPULATION = SHORT-TERM ILLUSION. MANIPULATION = LONG-TERM DESTRUCTION.

Repository: https://github.com/Zaineb-Gharib/yelp-analysis-project04/tree/member3-Hajar-Choukri
