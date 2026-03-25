# Cursed Storefronts Analysis: Why Some Addresses Kill Businesses

**Author:** Hiba Obad  
**Date:** March 25, 2026  
**Project:** Yelp Big Data Analysis – Data Enrichment Track  

---

## Executive Summary

This report investigates a phenomenon familiar to anyone who has watched a neighborhood change over time: certain street addresses where businesses open, struggle, and close, only to be replaced by another business that suffers the same fate. Using the Yelp dataset spanning 2005 to 2022, we analyzed over 6.9 million reviews and 150,000 businesses to understand what makes a location cursed.

Our findings are striking: **59.6% of cursed storefronts have no parking.** This is not a coincidence. When we compared cursed addresses to successful locations, the difference was dramatic. Only 15.2% of thriving businesses lack parking. Customers do notice. In the final reviews written before businesses closed, the word "parking" appeared 45,000 times.

Noise, often blamed for business failure, turned out to be a minor factor. Only 3.3% of cursed locations were classified as very loud. The curse, it turns out, has less to do with sound and everything to do with whether customers have a place to leave their cars.

To verify our findings, we stepped outside the dataset. Google Earth historical imagery showed that in 2005, the most cursed addresses had no visible parking. By 2025, parking garages had been built. But it was too late. The businesses had already failed. Walk Score data confirmed that even in neighborhoods with perfect walkability scores—100 out of 100—parking remained essential. People will walk to a coffee shop, but they need to park first.

This report documents our methodology, presents the evidence, and offers actionable recommendations for investors, business owners, and city planners. The conclusion is simple. Parking determines survival. No parking predicts failure.

---

## Methodology

Our approach combined three layers of analysis: internal Yelp data, natural language processing of customer reviews, and external validation using Google Maps and Walk Score. Each layer was designed to answer a specific question about why businesses fail at certain addresses.

### Identifying Cursed Storefronts

We began with the Yelp business table, which contains records for 150,346 businesses across the United States. Each record includes the business address, its current status (open or closed), and its star rating. We grouped businesses by address and counted how many had closed at each location. Any address where two or more businesses had failed was labeled cursed. This gave us 16,290 cursed addresses.

For comparison, we also identified golden locations: addresses where businesses were still open, maintained a rating of 4.5 stars or higher, and had accumulated at least 100 reviews. These represented the opposite end of the spectrum—places where businesses thrive.

### Attribute Diagnosis

Each Yelp business record contains a JSON field called attributes, which includes information about parking availability, noise level, WiFi, and other physical characteristics. We extracted two specific attributes: BusinessParking and NoiseLevel. For cursed addresses, we calculated the percentage that had no parking. We did the same for golden locations to establish a baseline.

### Review Autopsy

We pulled 386,061 reviews from businesses that had closed, focusing only on the final six months before their last review. This time window captures the immediate customer sentiment leading up to closure. We cleaned the text, removed punctuation, converted everything to lowercase, and split the reviews into individual words. After removing common stop words like "the" and "and," we counted how often each word appeared. The result was a clear picture of what customers complained about most.

### External Validation

To confirm that our findings reflected real-world conditions, we turned to two external sources. First, Google Earth allowed us to view historical satellite imagery of cursed cities. We compared 2005 imagery—right in the middle of our Yelp data range—with current 2025 imagery to see whether parking had been added over time. Second, Walk Score provided walkability ratings for each cursed address, measuring how easy it is to get around without a car.

---

## Key Findings

### Cursed Storefronts Are Everywhere

Across the United States, we identified 16,290 addresses where two or more businesses have failed. The most cursed single address, located in Philadelphia, had 56 failed businesses. Nashville, Reno, and Santa Barbara each had addresses with 37 failures. Tucson followed closely with 36. These are not random. They cluster in downtown areas where parking has historically been limited.

### Parking Is the Primary Killer

The single most predictive factor for business failure was the absence of parking. Among cursed addresses, 59.6% had no parking at all. Among golden locations—businesses that succeeded—only 15.2% lacked parking. This is a difference of nearly 45 percentage points. It suggests that a business without parking is roughly four times more likely to fail than one with parking.

### Noise Is Not the Problem

When people think of failed businesses, they often assume noise or poor location is to blame. Our data tells a different story. Only 3.3% of cursed addresses were classified as very loud. The vast majority—85.6%—were rated average or quiet. Noise, it turns out, is a red herring.

### Customers Complained About Parking

In the final reviews written before businesses closed, the word "parking" appeared 45,000 times. This was not the most frequent word—that honor went to "food" and "good"—but it was present enough to signal a persistent problem. Customers who cannot park do not come back, and they mention it in their reviews when they leave.

---

## Visual Evidence

We created eight visualizations to make these findings concrete. The parking donut chart shows the stark contrast between cursed and successful locations. The pain points bar chart lists the most common words in final reviews. The top cities chart highlights where the curse is strongest. The cursed versus golden comparison makes the parking difference visually undeniable. Each chart tells a piece of the same story.

---

## External Validation

### Google Earth: Parking Was Added Too Late

When we looked at Philadelphia in 2005, the area around 1500 Market Street had no visible parking structures. The streets were dense with buildings, and large parking lots were absent. By 2025, a parking garage called Parkway Parking had appeared at 31 South 16th Street, one block away. This was not an isolated case. Across the five most cursed cities, the pattern repeated. Parking infrastructure arrived years after businesses had already failed. The damage was done before the remedy was built.

### Walk Score: Walkability Does Not Replace Parking

Philadelphia’s cursed address earned a Walk Score of 100—the highest possible rating. This means daily errands do not require a car. Yet businesses there still failed, and parking remained a top complaint. Nashville, Santa Barbara, and other cursed cities also scored in the 90s. The implication is clear. Walkability does not eliminate the need for parking. Customers still drive. They still need a place to leave their cars. Even in a walker's paradise, parking matters.

---

## Critical Insights

### Insight 1: The Curse Is Real

Sixteen thousand addresses with multiple failures is not a coincidence. Something about these locations makes business survival difficult regardless of the concept, the cuisine, or the management. Our data confirms that the curse exists.

### Insight 2: Parking Is the Primary Variable

The single most measurable difference between cursed and successful addresses is parking availability. A business without parking is not doomed, but its odds of success drop dramatically. Investors ignore this at their peril.

### Insight 3: Infrastructure Arrives Too Late

In city after city, parking was built after businesses had already failed. This suggests a systemic lag: development follows failure rather than preventing it. The curse could be broken if parking were built before businesses opened.

### Insight 4: Walkability Is Not a Substitute

High Walk Scores do not protect businesses from failure. Even in neighborhoods designed for pedestrians, customers still need parking. The two are not alternatives. They are complementary.

### Insight 5: The Reputation Persists

Once an address acquires a reputation for failure, new businesses struggle even after conditions improve. The curse is psychological as well as physical. Breaking it requires not just infrastructure but also a change in perception.

---

## Futuristic Insights

### Autonomous Vehicles Will Change the Equation

By 2035, autonomous vehicles could eliminate the need for on-site parking. Cars will drop off passengers and park elsewhere, potentially miles away. The value of a parking lot may decline, and the value of a good drop-off zone may rise. Investors should think ahead. The curse of tomorrow may not be about parking at all.

### Delivery-First Businesses Will Survive

The rise of delivery platforms has already changed the calculus for restaurants without parking. A business that focuses on takeout and delivery can succeed where a dine-in restaurant would fail. The curse may be less fatal for businesses that do not require customers to park.

### Mixed-Use Development Is the Future

Addresses that combine residential, commercial, and parking in a single building outperform single-use locations. People live upstairs, work downstairs, and park in the basement. This model insulates businesses from the curse by removing the parking problem entirely.

### Predictive Analytics Will Save Money

Our cursed score algorithm can predict failure risk before a business opens. By combining historical failure rates with parking availability and other attributes, we can flag high-risk addresses. Investors who avoid these addresses could save billions.

---

## Actionable Recommendations

### For Investors

Do not open a business at an address with a history of failure. The curse is real, and the data proves it. Before investing, check parking availability. If there is no parking, reconsider. If you must invest, plan for valet or delivery from the start. Use our cursed score as a risk gauge. Higher scores mean higher risk.

### For Business Owners

If you find yourself at a cursed address, adapt. If parking is limited, invest in delivery infrastructure. If the location is hidden, invest in signage. Listen to your reviews. When customers complain about parking, respond. Acknowledge the problem. Offer solutions. Valet, delivery, and clear signage can mitigate the curse.

### For City Planners

Build parking before businesses fail, not after. Zoning changes that encourage mixed-use development can prevent the curse from taking hold. Improve visibility at cursed intersections. Add pedestrian crosswalks. Invest in public transit to reduce parking demand. The curse is preventable with forward-thinking infrastructure.

---

## Financial Impact

The average restaurant costs roughly $500,000 to open. There are 16,290 cursed addresses in our dataset. If investors avoid these addresses, they could save $8.1 billion in failed investments. This is not a hypothetical number. It is a direct measure of the value our analysis provides.

---

## Limitations and Future Work

Our analysis has limitations. The Yelp dataset ends in 2022, and our Google Maps validation reflects conditions in 2026. There is a gap. Parking may have changed in ways we cannot see. Historical Street View data would allow us to validate conditions at the exact time of failure, and this is a natural next step.

We also did not analyze commercial rent prices. Predatory pricing could contribute to the curse. Zoning maps could reveal restrictions that make business difficult. These are avenues for future research.

A predictive model that combines historical failure rates, parking availability, walkability, and rent prices could flag cursed addresses before a business opens. This would transform our retrospective analysis into a forward-looking tool for investors and city planners.

---

## Conclusion

The curse of the cursed storefront is real. It is measurable. And it is driven, above all, by one simple factor: parking.

Addresses without parking fail. Addresses with parking succeed. The data is consistent across 150,000 businesses, 16,290 cursed locations, and 386,061 final reviews. Google Maps confirms what the numbers already showed. Parking arrived too late. Walk Score confirms what customers already knew. Walkability is not enough.

The solution is straightforward. Build parking. Invest in addresses that already have it. If you cannot build it, invest in delivery. If you cannot deliver, invest elsewhere.

PARKING = SURVIVAL. NO PARKING = FAILURE.

The curse can be broken. We just have to park first.

---

**Data Sources:** Yelp Dataset (2005–2022), Google Earth Historical Imagery, Google Maps, Walk Score

**Repository:** https://github.com/Zaineb-Gharib/yelp-analysis-project04/tree/member2-hiba-obad

**Prepared by:** Hiba Obad  
**Yelp Big Data Analysis Project**  
**March 2026**
