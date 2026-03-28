# Zeppelin Notebooks - Yelp Analysis

## Files

| File | Description |
|------|-------------|
| `user_analysis_charts.zpln` | User behavior analysis: user growth, elite trend, top reviewers, rating distribution, adventurous eaters |
| `Cursed Storefronts Charts_2MPPSPFS6.zpln` | Cursed storefronts analysis: 8 charts on parking, pain points, cities, noise, risk matrix, cumulative failures |
| `comprehensive_analysis_charts.zpln` | Business success analysis: top merchants, success score formula, conversion rate, cursed diagnosis, NLP pain points |

## What's Inside

### User Analysis Notebook
- User growth over time
- Elite users trend (30% → 0%)
- Top reviewers (Fox: 17,473 reviews)
- Most popular users (Mike: 12,497 fans)
- Rating distribution (46% 5-star)
- Adventurous eaters (15+ cuisines)

### Cursed Storefronts Notebook
- Chart 1: Parking Donut (59.6% no parking)
- Chart 2: Pain Points - Top words in reviews
- Chart 3: Top Cursed Cities (Philadelphia: 56 failures)
- Chart 4: Noise Level Pie (only 3.3% very loud)
- Chart 5: Cursed vs Golden comparison
- Chart 6: Failure Rate by Parking Type
- Chart 7: Risk Matrix (Parking vs Noise)
- Chart 8: Cumulative Failures over time
- Word cloud and summary dashboard

### Comprehensive Analysis Notebook
- Top 5 merchants per city
- Success score formula: Stars (40%) + Reviews (30%) + Check-ins (30%)
- Review conversion rate by business stage
- Cursed storefronts diagnosis (parking vs noise)
- NLP pain points extraction

## How to Use
1. Import .zpln file into Zeppelin
2. Ensure Hadoop is running (`start-dfs.sh`, `start-yarn.sh`)
3. Ensure Yelp data is in HDFS at `/yelp/data/`
4. Run paragraphs in order
5. Charts save to `/data/charts/`

## Data Source
- Yelp dataset stored in HDFS at `/yelp/data/`
- Tables: business, review, users, checkin

## Author
Hiba Obad
March 2026
