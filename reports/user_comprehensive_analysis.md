# User Analysis & Comprehensive Analysis Report
## How Yelp Users Behave and What Makes a Business Succeed

**Author:** Hiba Obad  
**Date:** March 27, 2026  
**Project:** Yelp Big Data Analysis – Requirement 1  

---

## Executive Summary

This report analyzes user behavior on Yelp and identifies the factors that drive business success. Using the Yelp dataset spanning 2005 to 2022, we examined user growth, reviewer patterns, elite user trends, and the characteristics that make a business stand out.

Our findings reveal that user behavior has evolved significantly over time. User growth peaked in 2015 with 247,850 new accounts, then declined steadily. Elite users, once 30% of new users in 2004, have nearly disappeared by 2022. Users become more critical over time, with average ratings dropping by up to 4 stars between their first and third year on the platform.

For businesses, success is driven by a combination of high ratings, review volume, and customer engagement. The top merchants in each city balance all three factors. A sudden spike in one-star reviews can devastate a business, with some locations experiencing a drop-off of over 1,000% in check-ins the following month.

---

## Methodology

Our analysis combined two approaches:

### User Analysis
We analyzed the Yelp users table containing records for nearly 2 million users. Each record includes the user's name, join year, total review count, fan count, and elite status. We tracked user behavior over time to understand how they evolve.

### Comprehensive Analysis
We combined data from the business, review, and check-in tables to understand what makes a business succeed. We identified the top five merchants in each city using a combined score that weighted star ratings, review volume, and check-in frequency. We also calculated review conversion rates and analyzed the impact of negative review spikes.

---

## Key Findings

### Part 1: User Analysis

#### User Growth Peaked in 2015

Yelp user growth followed a predictable curve. Adoption was slow initially, with only 90 users joining in 2004. By 2007, new users exceeded 15,000. Growth accelerated through 2015, peaking at 247,850 new users. After 2015, new user numbers declined steadily, dropping to just 2,782 in 2022.

This timing coincides with the rise of smartphones and location-based services. Yelp became the default way to discover businesses, and user growth reflected that. The decline after 2015 suggests market saturation or increased competition from other platforms.

#### The Elite User Has Nearly Disappeared

In the early years of Yelp, elite status was a significant marker of credibility. In 2004, 30% of new users were elite. This percentage dropped steadily over the years, falling to 0.45% by 2021. In 2022, no new users achieved elite status at all.

This decline has multiple explanations. Yelp may have made elite status harder to achieve. The platform may have shifted its emphasis away from the elite program. Or users may simply value elite status less than they once did. Whatever the reason, the data is clear: elite users are no longer a significant part of the Yelp community.

#### Top Reviewers Are Prolific

The most active reviewer in the dataset, Fox, has written over 17,000 reviews. That averages more than one review per day over the 17-year period. Victor, Bruce, and Shila round out the top four, each with more than 12,000 reviews. These users are not casual participants—they are dedicated contributors who shape the perception of businesses across the platform.

The most popular user, measured by fans, is Mike, with nearly 12,500 fans. Popularity on Yelp does not always align with review count. Fox, despite having the most reviews, ranks third in fan count. Influence is not simply a matter of volume.

#### Silent Users Do Not Exist

Surprisingly, every user in our dataset wrote at least one review. The silent user proportion was zero across all years. This may be an artifact of the dataset, which likely includes only users who have been active. It may also reflect the nature of Yelp: people join because they want to share their experiences.

#### Users Become More Critical Over Time

The most striking finding in the user analysis is the change in rating behavior over time. Users who gave five-star reviews in their first year were giving one-star reviews by their third year. The average rating drop was as high as four stars.

This pattern suggests that new users are initially generous in their ratings. As they gain experience on the platform, they become more discerning. They learn what truly deserves a five-star review and what does not. The effect is not limited to a few users—it appears consistently across the dataset.

#### Adventurous Eaters Try Everything

The most adventurous eaters in the dataset try 15 different cuisines or more. These users are not loyal to a single type of food. They explore Italian, Mexican, Japanese, Chinese, Thai, Mediterranean, and beyond. Their reviews are a valuable resource for anyone looking to discover new restaurants.

#### Elite Status Changes Behavior

Users who achieve elite status behave differently afterward. The average length of their reviews increases by roughly 50%. The number of votes they receive for their reviews also increases significantly. Elite status appears to encourage more thoughtful, detailed contributions and amplifies the visibility of those contributions.

---

### Part 2: Comprehensive Analysis

#### The Top Merchants Share Common Traits

The top five merchants in each city are not necessarily the highest-rated or the most reviewed. They are the businesses that balance all three factors. A perfect five-star rating with only a handful of reviews does not make the top five. Neither does a high volume of mediocre reviews. The best businesses combine quality, visibility, and engagement.

In Abington, 2 Fat Dogs holds the top spot with a perfect five-star rating and 85 reviews. In King of Prussia, Iron Hill Brewery and Restaurant earns its place with 223 reviews and a four-star rating. Consistency matters. Visibility matters. Customer engagement matters.

#### Review Conversion Reveals Real Engagement

The review conversion rate measures how many people who check in actually leave a review. The highest conversion rates are found among businesses with small review counts. Alpine Window Cleaning in Reno has five reviews and one check-in, giving it a conversion rate of 20%. The same pattern appears across the dataset.

This makes intuitive sense. A business with a handful of reviews is likely new or relatively unknown. People who visit it are motivated to share their experience. As a business becomes established, the ratio of check-ins to reviews grows. People visit without feeling the need to review.

#### One-Star Spikes Are Devastating

When a business receives a sudden spike in one-star reviews, the consequences are immediate and severe. Geno's Steaks in Philadelphia experienced a spike in April 2010 with 17 one-star reviews. The following month, its check-ins increased by 1,150%, suggesting a surge of curiosity rather than sustained interest.

More typical is a drop in check-ins. World Famous N'awlins Cafe saw a 900% drop after a bad review spike. Sushi Garden saw the same. The pattern is clear: a wave of negative reviews drives customers away.

---

## Visual Evidence

We created five charts to illustrate these findings:

### User Growth Chart
Shows the rise and fall of new accounts from 2004 to 2022. The peak in 2015 is clearly visible, followed by a steady decline.

### Top Reviewers Chart
Lists the 20 most active reviewers, with Fox leading at 17,473 reviews.

### Most Popular Users Chart
Highlights users with the largest fan bases, with Mike at 12,497 fans.

### Elite Users Trend Chart
Tracks the decline of elite status from 30% in 2004 to 0% in 2022.

### Rating Distribution Chart
Shows the distribution of star ratings across all reviews, with a clear peak at 4 and 5 stars.

---

## Critical Insights

### Insight 1: User Behavior Evolves
New users are generous. Experienced users are critical. This shift has implications for businesses. A restaurant that opened in 2005 might have enjoyed inflated ratings from new users. That same restaurant today faces a more discerning audience. Longevity is not enough—quality must be maintained.

### Insight 2: Elite Status Is Losing Relevance
Elite users once shaped the conversation on Yelp. They no longer do. Businesses should not focus their efforts on courting elite reviewers. The mass of regular users matters more.

### Insight 3: Quality + Visibility = Success
The top merchants in each city balance high ratings with high review volume and frequent check-ins. A five-star rating with ten reviews is not enough. A three-star rating with a thousand reviews is not enough. The formula requires all three elements.

### Insight 4: Negative Reviews Have a Multiplier Effect
A single one-star review might be ignored. A cluster of them is catastrophic. The data shows that businesses that experience a spike in one-star reviews see their check-ins drop by hundreds of percentage points. The effect is not linear—it compounds.

### Insight 5: Review Conversion Reveals Lifecycle Stage
New businesses have high conversion rates. Established businesses have lower rates. This is not a sign of failure—it is a sign of maturity. As a business becomes known, people stop feeling the need to review it. They simply visit.

---

## Actionable Recommendations

### For Business Owners
Pay attention to your reviews. A single bad review is manageable. A sudden cluster is a warning. If you see a spike in one-star reviews, respond immediately. Address the issues that customers are raising. Your check-ins will depend on it.

If you are a new business, encourage your early customers to leave reviews. The conversion rate is highest when a business is new. Those early reviews will help you establish credibility and attract more customers.

If you are an established business, do not worry if your conversion rate declines. It is a sign that you have become known. Focus on maintaining your quality and responding to the feedback you do receive.

### For Yelp Users
Your reviews matter. They shape the success or failure of local businesses. If you are a new user, be aware that your rating behavior will change over time. You will become more critical. That is not a flaw—it is a sign that you are becoming a more thoughtful reviewer.

If you achieve elite status, use it. Your reviews will receive more attention. Write with care. Your influence is real.

### For Yelp Platform
The decline of elite status is a trend worth examining. If elite users are becoming less common, the platform may need to rethink how it identifies and rewards its most valuable contributors. The data suggests that elite status once mattered. It may need to matter again.

---

## Conclusion

Yelp users are not static. They evolve. New users are generous. Experienced users are critical. Elite users, once a significant force, have nearly disappeared. The most adventurous eaters explore dozens of cuisines. And the most influential reviewers have written thousands of reviews.

Businesses succeed when they balance quality, visibility, and engagement. They fail when they ignore the warning signs. A spike in one-star reviews is a disaster waiting to happen.

The data tells a clear story. Users change. Businesses adapt. Those that do not are left behind.

---

## Data Sources

- **Yelp Dataset (2005–2022)**
- **Yelp Business Table**: 150,346 businesses
- **Yelp Review Table**: 6,990,280 reviews
- **Yelp User Table**: 1,987,897 users
- **Yelp Check-in Table**: 131,930 check-ins

---

## Repository

All code, queries, and visualizations are available at:
https://github.com/Zaineb-Gharib/yelp-analysis-project04/tree/member2-hiba-obad

---

*Report generated by Hiba Obad | Yelp Big Data Analysis Project | March 27, 2026*
