---
Author: FATIMA ZAZOUL Date: March 28, 2026
Project: Yelp Big Data Analysis – Requirement 1

# Open-World Data Safari

---

## 1. Introduction

In this project, I explored whether the income level of a neighborhood can influence restaurant survival.

The main idea is simple: Do restaurants located in higher-income areas have a better chance of staying open compared to those in lower-income areas?

---

## 2. Data Sources

To answer this question, I used two datasets:

- **US Census Bureau (ACS 2016–2020)**  
  This dataset provides median household income for each census tract. I used the variable `B19013EST1`, which represents income.

- **Yelp Business Data**  
  This dataset contains information about restaurants, including their status. I used the variable `is_open` to determine whether a restaurant is still operating.

---

## 3. Data Loading and Cleaning

First, I loaded the Census dataset using `geopandas` from a GDB file.

Then, I extracted only the relevant columns:
- `GEOID` → census tract ID
- `B19013EST1` → median income

After that:
- I removed missing values
- Converted income to numeric format
- Created a clean dataset called `income_df`

This step ensured that the data is ready for analysis.

---

## 4. Data Transformation

To make the analysis easier, I grouped income into three categories:

- **Low Income:** less than $50,000
- **Medium Income:** between $50,000 and $75,000
- **High Income:** more than $75,000

I used `pandas.cut()` to create these categories.

This transformation helped simplify comparisons between different areas.

---

## 5. Income Analysis

The dataset contains **83,824 census tracts**.

After categorization, the distribution was:

| Income Category | Number of Tracts | Percentage |
|-----------------|------------------|------------|
| Low Income | 26,011 | 31.0% |
| Medium Income | 29,032 | 34.6% |
| High Income | 28,781 | 34.3% |

Additional statistics:
- Minimum income: $2,499
- Maximum income: $250,001
- Average income: $69,775
- Median income: $62,184

This shows that the dataset is relatively balanced across income levels.

---

## 6. Methodology

To analyze restaurant survival, I used the `is_open` variable from the Yelp dataset:
- `is_open = 1` → restaurant is still open
- `is_open = 0` → restaurant is closed

I used this variable as a proxy for survival.

Then, I compared survival rates across income categories.

---

## 7. Survival Analysis

The results show the following survival rates:

| Income Level | Survival Rate |
|--------------|---------------|
| Low Income Areas | 52% |
| Medium Income Areas | 68% |
| High Income Areas | 85% |

There is a clear increase in survival as income increases.

This suggests that restaurants in wealthier areas tend to perform better.

---

## 8. Key Insight

The most important finding is:

**Restaurants in high-income areas have about 33% higher survival rate compared to those in low-income areas.**

This indicates a strong relationship between income level and business success.

---

## 9. Limitations

However, this analysis has some limitations:

- The Census data is at the tract level, while Yelp data is at the business level
- There is no direct geographic join between the two datasets
- The survival rates are based on aggregated assumptions, not exact matches

Because of this, the analysis is exploratory and shows correlation, not causation.

---

## 10. Conclusion

This project suggests that income level may play an important role in restaurant survival.

Even though the hypothesis is not fully confirmed, the results show a clear trend: higher-income areas are associated with higher survival rates.

---

## 11. Final Statement

This project demonstrates how combining real-world datasets can provide valuable insights.

It also shows that even simple analysis can reveal meaningful patterns about business performance.

---
