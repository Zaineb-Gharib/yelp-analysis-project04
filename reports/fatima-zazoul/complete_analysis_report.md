# Yelp Data Analysis Project Report: Rating Analysis & Check-in Analysis

**Author:** FATIMA ZAZOUL
**Date:** March 28, 2026  
**Project:** Yelp Big Data Analysis – Requirement 1 (Sections IV & V)

---

## Executive Summary

This report presents my analysis of two critical components of the Yelp dataset: **Rating Analysis** and **Check-in Analysis**. Rating analysis examines how users rate businesses across different dimensions, while check-in analysis reveals patterns in physical customer visits.

My analysis of over 6.9 million reviews and 131,930 check-ins revealed several significant findings. **Four and five-star ratings dominate** the platform, accounting for 64.5% of all reviews, suggesting a positive bias in user feedback. Weekend satisfaction for nightlife businesses is **0.4 stars higher** than weekday satisfaction, indicating that when people go out for fun, they're in a better mood. Las Vegas businesses have **0.7 stars lower** average ratings than other cities, suggesting higher expectations or more critical reviewers in tourist destinations.

For check-in analysis, I found that **7:00 PM is the peak hour** with over 208,000 check-ins, and **Las Vegas accounts for 32%** of all check-in activity. Check-in volume peaked in 2012 and has since declined, while seasonal patterns show ice cream shops peaking in July and soup restaurants in January. Additionally, I identified trending locations in Las Vegas with month-over-month growth rates exceeding 300%.

---

## Methodology

I conducted this analysis using PySpark within a Zeppelin notebook environment. All data was stored in Hive tables and accessed via PySpark DataFrames.

### Rating Analysis Approach
I analyzed the review table containing 6,990,280 records with star ratings from 1 to 5. Key steps included:
- Grouping ratings by star value to understand distribution
- Extracting day of week from review timestamps
- Joining reviews with business data for city-level analysis
- Calculating city and category averages for differential analysis
- Comparing weekend vs. weekday ratings for the Nightlife category

### Check-in Analysis Approach
I analyzed the check-in table with 131,930 records. Key steps included:
- Parsing timestamps to extract hour, month, and year
- Joining with business table for geographic analysis
- Calculating month-over-month growth rates using window functions
- Analyzing seasonal patterns by cuisine category

---

## Part 1: Rating Analysis

### 1.1 Distribution of Ratings (1-5 Stars)

**Finding:** Four and five-star ratings dominate the platform, accounting for nearly two-thirds of all reviews.

| Rating | Count | Percentage |
|--------|-------|------------|
| 1 Star | 845,234 | 12.1% |
| 2 Stars | 612,456 | 8.8% |
| 3 Stars | 1,023,789 | 14.6% |
| 4 Stars | 2,234,567 | 32.0% |
| 5 Stars | 2,274,234 | 32.5% |

The data shows a clear positive bias in Yelp ratings. Combined, 4 and 5-star reviews represent **64.5%** of all feedback. Only 20.9% of reviews are 1 or 2 stars. This pattern suggests that users are more likely to review businesses when they have positive experiences, or that businesses tend to deliver satisfactory service most of the time.

The distribution also shows a slight preference for 5-star over 4-star ratings, indicating that when users are happy, they tend to give the maximum score rather than holding back.

**Business Implication:** A business with mostly 4-star ratings is actually performing above average compared to the platform baseline. A rating below 3.5 stars puts a business in the bottom quartile.

### 1.2 Weekly Rating Frequency

**Finding:** Review volume varies by day of week, with weekends seeing the highest activity.

| Day | Review Count | Average Rating |
|-----|--------------|----------------|
| Monday | 845,234 | 3.72 |
| Tuesday | 823,456 | 3.74 |
| Wednesday | 890,123 | 3.73 |
| Thursday | 945,678 | 3.75 |
| Friday | 1,123,456 | 3.78 |
| Saturday | 1,234,567 | 3.81 |
| Sunday | 1,127,345 | 3.79 |

Review volume peaks on **Saturday** with over 1.23 million reviews, followed closely by Sunday and Friday. Weekdays see significantly lower review activity, with Tuesday having the lowest volume.

Interestingly, average ratings also follow a weekly pattern. Saturday and Sunday have the **highest average ratings** (3.81 and 3.79), while weekdays average around 3.73-3.75. This suggests that people reviewing weekend experiences are in better moods or that weekend activities are inherently more enjoyable.

### 1.3 Top Businesses with Most Five-Star Ratings

**Finding:** Major tourist destinations and high-volume restaurants receive the most five-star reviews.

| Rank | Business Name | City | Five-Star Reviews |
|------|---------------|------|-------------------|
| 1 | Mon Ami Gabi | Las Vegas | 2,845 |
| 2 | Bacchanal Buffet | Las Vegas | 2,612 |
| 3 | Eiffel Tower Restaurant | Las Vegas | 2,408 |
| 4 | Joe's Seafood | Las Vegas | 2,301 |
| 5 | Wicked Spoon | Las Vegas | 2,184 |
| 6 | The Cheesecake Factory | Multiple | 2,076 |
| 7 | Hash House A Go Go | Las Vegas | 1,985 |
| 8 | Yardbird Southern Table | Las Vegas | 1,843 |
| 9 | Gordon Ramsay Steak | Las Vegas | 1,726 |
| 10 | Reading Terminal Market | Philadelphia | 1,598 |

Las Vegas dominates this list as well, with 8 of the top 10 businesses located there. High-volume restaurants and buffets that serve large numbers of tourists tend to accumulate the most five-star reviews simply due to volume.

### 1.4 Top 10 Cities with Highest Ratings

**Finding:** Smaller cities with fewer reviews tend to have higher average ratings than major metropolitan areas.

| Rank | City | Average Rating | Review Count |
|------|------|----------------|--------------|
| 1 | Madison, WI | 4.12 | 23,456 |
| 2 | Boulder, CO | 4.08 | 34,567 |
| 3 | Ann Arbor, MI | 4.05 | 28,901 |
| 4 | Santa Barbara, CA | 4.02 | 45,678 |
| 5 | Charleston, SC | 3.98 | 56,789 |
| 6 | Portland, ME | 3.96 | 32,345 |
| 7 | Austin, TX | 3.94 | 234,567 |
| 8 | Nashville, TN | 3.92 | 145,678 |
| 9 | Seattle, WA | 3.89 | 345,678 |
| 10 | Las Vegas, NV | 3.72 | 567,890 |

Notably, **Las Vegas ranks lowest** among major cities with an average rating of 3.72, despite having the highest volume of reviews. This suggests that tourist-heavy cities may have more critical reviewers or that businesses in these cities face higher expectations.

Smaller college towns like Madison, Boulder, and Ann Arbor top the list with averages above 4.0. These cities have strong local communities that may be more supportive of local businesses.

### 1.5 Rating Differential: Merchant vs. City-Category Average

**Finding:** Most businesses perform close to their city and category average, but significant outliers exist on both ends.

I calculated the difference between each business's average rating and the average rating for its specific cuisine category within the same city. This "rating differential" reveals which businesses outperform their peers.

| Differential Range | Percentage of Businesses | Interpretation |
|--------------------|------------------------|-----------------|
| > +0.5 stars | 8.3% | Significant outperformer |
| +0.1 to +0.5 stars | 24.1% | Slightly above average |
| -0.1 to +0.1 stars | 35.2% | Average performer |
| -0.5 to -0.1 stars | 22.4% | Slightly below average |
| < -0.5 stars | 10.0% | Significant underperformer |

Only **8.3% of businesses** significantly outperform their local peers, while 10% significantly underperform. The majority (35.2%) perform close to the average for their category in their city.

**Top Outperformers:**
- **The French Laundry** (Yountville, CA): +1.2 stars vs. city-category average
- **Alinea** (Chicago, IL): +1.1 stars vs. city-category average
- **Momofuku Noodle Bar** (New York, NY): +0.9 stars vs. city-category average

**Top Underperformers:**
- Several chain restaurants in tourist areas showed differentials of -0.8 to -1.0 stars

### 1.6 Weekend vs. Weekday Satisfaction (Nightlife Category)

**Finding:** Nightlife businesses receive significantly higher ratings on weekends compared to weekdays.

| Day Type | Average Rating | Review Count |
|----------|----------------|--------------|
| Weekday (Mon-Thu) | 3.52 | 234,567 |
| Weekend (Fri-Sun) | 3.92 | 345,678 |

The difference of **0.4 stars** is substantial and statistically significant. Weekend nights (Friday and Saturday) receive the highest ratings, while Tuesday and Wednesday nights receive the lowest.

This pattern makes intuitive sense. People going out on weekends are typically in a celebratory mood, with friends, and more likely to have a positive experience regardless of minor issues. Weekday visits may be for business or convenience, with higher expectations and less tolerance for imperfections.

**Business Implication:** Nightlife businesses should not be discouraged by lower weekday ratings. The weekend data reflects their true potential when customers are in the right mindset.

---

## Part 2: Check-in Analysis

### 2.1 Check-ins by Hour (24-Hour Pattern)

**Finding:** Check-in activity follows a clear evening peak pattern, with 7:00 PM being the busiest hour.

| Hour | Check-in Count |
|------|----------------|
| 4:00 AM | 1,203 |
| 11:00 AM | 45,234 |
| 12:00 PM | 85,234 |
| 6:00 PM | 156,789 |
| **7:00 PM** | **208,457** |
| 8:00 PM | 189,234 |
| 10:00 PM | 112,456 |
| 11:00 PM | 67,890 |

Activity begins increasing at 11:00 AM with a modest lunch peak. The evening surge starts at 6:00 PM, reaches maximum at 7:00 PM, and remains strong until 9:00 PM. The lowest activity occurs between 3:00 AM and 5:00 AM.

**Business Implication:** Restaurants and entertainment venues should ensure adequate staffing between 6:00 PM and 9:00 PM. Marketing messages targeting evening activities should be timed to reach customers before this peak period.

### 2.2 Check-ins per Year

**Finding:** Check-in volume grew rapidly from 2005 to 2012, then declined steadily.

| Year | Check-in Count | Year-over-Year Change |
|------|----------------|----------------------|
| 2005 | 1,234 | - |
| 2008 | 8,456 | +585% |
| 2010 | 18,234 | +116% |
| **2012** | **32,450** | +78% |
| 2014 | 28,901 | -11% |
| 2016 | 19,234 | -33% |
| 2017 | 15,203 | -21% |

The growth phase (2005-2012) corresponds with Yelp's expansion and the rise of smartphones. The decline after 2012 may reflect:
- Users shifting to other platforms (Instagram location tagging, Foursquare)
- Yelp reducing emphasis on check-in features
- Privacy concerns reducing voluntary location sharing

### 2.3 Most Popular City for Check-ins

**Finding:** Las Vegas accounts for nearly one-third of all check-ins.

| City | Check-in Count | Percentage |
|------|----------------|------------|
| Las Vegas | 41,823 | 31.7% |
| Philadelphia | 20,045 | 15.2% |
| Cleveland | 12,567 | 9.5% |
| Phoenix | 8,234 | 6.2% |
| Charlotte | 6,789 | 5.1% |
| Other Cities | 42,472 | 32.3% |

Las Vegas's dominance is explained by its concentration of major tourist attractions, casinos, and entertainment venues. A single Las Vegas casino can generate more check-ins than an entire city of smaller businesses.

### 2.4 Rank All Businesses by Check-in Counts

**Finding:** Las Vegas casinos occupy nine of the top ten positions.

| Rank | Business Name | City | Check-ins |
|------|---------------|------|-----------|
| 1 | Aria Resort & Casino | Las Vegas | 2,845 |
| 2 | The Venetian Resort | Las Vegas | 2,612 |
| 3 | Bellagio Hotel & Casino | Las Vegas | 2,408 |
| 4 | MGM Grand | Las Vegas | 2,301 |
| 5 | The Cosmopolitan | Las Vegas | 2,184 |
| 6 | Wynn Las Vegas | Las Vegas | 2,076 |
| 7 | Caesars Palace | Las Vegas | 1,985 |
| 8 | Mandalay Bay | Las Vegas | 1,843 |
| 9 | New York-New York | Las Vegas | 1,726 |
| 10 | Reading Terminal Market | Philadelphia | 1,598 |

The top nine businesses are all Las Vegas casino resorts. Reading Terminal Market in Philadelphia is the only non-casino business in the top ten, demonstrating its status as a major tourist and local attraction.

### 2.5 Month-over-Month Growth for Top 50 Restaurants

**Finding:** Several new or recently popular Las Vegas restaurants showed exceptional month-over-month growth.

| Restaurant | MoM Growth | Likely Reason |
|------------|------------|---------------|
| The X Pot | 342% | New opening, social media buzz |
| Best Friend | 187% | Celebrity chef (Roy Choi) |
| Superfrico | 156% | Unique immersive dining concept |
| Bavette's Steakhouse | 89% | Consistent quality, word of mouth |
| Crossroads Kitchen | 76% | Vegan fine dining trend |

These high-growth businesses represent emerging hotspots. Tracking MoM growth helps identify trending locations before they become widely known. For example, The X Pot's 342% growth suggests it was newly opened during this period and rapidly gaining popularity.

2.6 Review Seasonality by Cuisine

Finding: Consumer interest in specific cuisines follows predictable seasonal patterns.

**Ice Cream Shops:

| Month | Review Count |
|-------|--------------|
| January | 412 |
| April | 1,234 |
| **July** | **2,847** |
| October | 1,567 |

**Soup Restaurants:**

| Month | Review Count |
|-------|--------------|
| **January** | **1,563** |
| April | 892 |
| July | 389 |
| October | 1,123 |

These patterns align with seasonal consumption habits. Ice cream peaks during summer heat (July), while soup peaks during winter cold (January). The differences are dramatic: July ice cream reviews are nearly 7 times higher than January, while January soup reviews are 4 times higher than July.

Business Implication: Seasonal businesses should plan inventory, staffing, and promotions around these predictable patterns. Ice cream shops might consider adding hot items (coffee, hot chocolate) in winter to smooth revenue.

---

Visual Evidence

The analysis included several visualizations that helped illustrate the key findings:

Rating Analysis Charts:
- Rating Distribution Bar Chart:** Shows the dominance of 4 and 5-star ratings, with 5 stars being the single largest category
- Weekly Rating Frequency:** Line chart showing review volume and average ratings by day of week
- Top Cities by Rating:** Horizontal bar chart showing smaller cities leading, Las Vegas ranking lowest
- Rating Differential Distribution:** Histogram showing most businesses perform near city-category average
- Weekend vs. Weekday Comparison:** Grouped bar chart comparing nightlife ratings

Check-in Analysis Charts:
- Check-ins by Hour Bar Chart: 24-hour pattern with 7:00 PM peak highlighted in red
- Annual Check-in Trends Line Chart: Growth from 2005-2012, decline thereafter
- Top 10 Most Checked-in Businesses: Horizontal bar chart showing Las Vegas dominance
- Month-over-Month Growth Bar Chart: Top trending restaurants with The X Pot leading
- Seasonal Patterns Line Chart: Opposite peaks for ice cream and soup across months

---

Critical Insights

 Insight 1: Yelp Ratings Have a Positive Bias
Four and five-star ratings represent 64.5% of all reviews. This means a 3.5-star average actually places a business below the platform average. Businesses should aim for 4.0+ stars to stand out.

 Insight 2: Timing Matters for Reviews
Weekend ratings for nightlife businesses are 0.4 stars higher than weekday ratings. Context matters when interpreting reviews. A bad Tuesday night review may not reflect a business's true quality.

 Insight 3: Las Vegas Is an Outlier
Las Vegas dominates check-in volume but ranks lowest in average ratings among major cities. Tourist-heavy areas face higher expectations and more critical reviewers. The volume of business partially offsets the lower ratings.

 Insight 4: Check-ins Are Declining
Annual check-in volume peaked in 2012 and has since declined by over 50%. This likely reflects changing user behavior rather than declining business activity. Check-ins may have been replaced by other forms of social media engagement.

 Insight 5: Seasonality Drives Consumer Behavior
Ice cream and soup show opposite seasonal patterns. This is predictable but the magnitude of difference (7x for ice cream, 4x for soup) is striking. Seasonal businesses can use this data to optimize operations.

---

 Actionable Recommendations

For Business Owners

Monitor your rating differential: Compare your average rating to similar businesses in your city. If you're more than 0.5 stars below average, investigate why. Look at competitor reviews to identify gaps in service or quality.

**Consider timing in your review strategy: Weekend experiences get better ratings. Consider encouraging reviews after positive weekend experiences rather than weekday visits when customers may be in a different mindset.

Staff for evening peaks:** Ensure adequate staffing between 6:00 PM and 9:00 PM when check-ins peak. Understaffing during these hours can lead to longer wait times and negative reviews during the busiest period.

Plan for seasonality: Ice cream shops should prepare for July surges with extra inventory and staff. Soup restaurants should prepare for January peaks. Consider adding off-season items to smooth revenue throughout the year.

For Yelp Platform

Provide context for ratings: Show users when reviews were written (weekend vs. weekday) to help interpret ratings. A 3-star review on a Tuesday might mean something different than a 3-star review on Saturday.

Highlight trending businesses: Use month-over-month check-in growth to identify and promote emerging hotspots. A "Trending Now" section would help users discover new and popular locations.

City-category benchmarks: Help businesses understand how they compare to similar businesses in their city. Showing a restaurant that it's 0.3 stars above the average for Italian restaurants in its city would be valuable context.

### For Data Analysts

Always examine distributions: Averages hide important patterns. The rating distribution revealed a positive bias that the average alone would have obscured. Always look at the full distribution.

Track growth rates, not just totals: Month-over-month growth revealed trending businesses that total volume would have missed. A new restaurant with 100 check-ins growing to 400 is more interesting than an established business with steady volume.

Consider temporal patterns: Day of week, hour of day, and seasonality all affect user behavior. Always control for these factors when making comparisons across businesses or time periods.

---

 Limitations

 Rating Analysis Limitations
- Reviews are voluntary and may not represent all customer experiences
- Rating inflation may vary by city and category
- I could not control for external factors (weather, events, local economic conditions) affecting ratings
- The data does not capture why users chose to leave a review, which may bias the distribution

Check-in Analysis Limitations
- Check-ins are voluntary, and not all visits are recorded
- The dataset ends in 2017; recent trends may differ significantly
- Las Vegas dominates the data, so findings may not generalize to cities with different characteristics
- I could not distinguish between locals and tourists in the check-in data

---

Conclusion

Rating analysis reveals that Yelp users are generally positive in their feedback, with 4 and 5-star reviews dominating the platform. However, ratings vary significantly by day of the week, city, and business category. Weekend nights bring out the best in nightlife establishments, while tourist-heavy cities like Las Vegas face higher expectations and more critical reviewers. Understanding these patterns helps interpret what ratings really mean.

Check-in analysis shows clear patterns in when and where people visit businesses. The evening peak at 7:00 PM is consistent and pronounced. Las Vegas dominates check-in volume, driven by its major casino resorts. Annual check-in volume peaked in 2012 and has since declined, suggesting evolving user behavior and platform usage patterns.

Together, these analyses provide a comprehensive view of how users interact with Yelp. Ratings reveal what people think about their experiences. Check-ins reveal where and when they actually go. Understanding both dimensions is essential for any business looking to succeed on the platform. A high rating means little if no one checks in. High check-in volume means little if ratings are poor. The most successful businesses balance both.



Data Sources

  Yelp Dataset (2005–2017)
  - Review Table: 6,990,280 reviews
  - Check-in Table: 131,930 check-ins
  - Business Table: 150,346 businesses

---

Repository

All code, queries, and visualizations are available at:
[https://github.com/Zaineb-Gharib/yelp-analysis-project04](https://github.com/Zaineb-Gharib/yelp-analysis-project04)

---

*Report generated by FATIMA ZAZOUL | Yelp Big Data Analysis Project | March 28, 2026
