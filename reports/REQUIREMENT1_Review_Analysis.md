Review Analysis: Understanding Yelp Review Patterns
Author: Hajar Choukri
Date: March 27, 2026
Project: Yelp Big Data Analysis – Requirement 1
________________________________________
What I Did
For this requirement, I analyzed Yelp reviews to understand user behavior and review patterns. I used PySpark on the Yelp dataset (about 7 million reviews). My goal was to answer questions like: How do reviews change over time? What words appear most often? Do angry customers write more?
________________________________________
How I Did It (Step by Step)
1. Setting Up the Data
I loaded the review data from HDFS into a PySpark dataframe:
python
review_df = spark.read.parquet("/yelp/review")
This gave me about 7 million rows. I checked the schema to understand what columns I had: user_id, business_id, stars, text, useful, funny, cool, date.
2. Reviews Per Year
I extracted the year from the date column and grouped by year:
python
from pyspark.sql.functions import year, count
yearly_reviews = review_df.groupBy(year("date").alias("year")).agg(count("*").alias("review_count"))
I ordered by year and saved the result to a CSV. The challenge was handling null dates, but I found only a few and dropped them.
3. Useful, Funny, Cool Counts
This was straightforward - just sum each column:
python
engagement = review_df.agg(
    sum("useful").alias("total_useful"),
    sum("funny").alias("total_funny"),
    sum("cool").alias("total_cool")
)
4. Top Users Per Year
This was trickier. I needed to rank users by review count for each year:
python
from pyspark.sql.window import Window
from pyspark.sql.functions import rank

user_yearly = review_df.groupBy("user_id", year("date").alias("year")).agg(count("*").alias("review_count"))
window = Window.partitionBy("year").orderBy(col("review_count").desc())
top_users = user_yearly.withColumn("rank", rank().over(window)).filter(col("rank") <= 5)
5. Text Analysis (Most Common Words)
This was the hardest part. I had to:
•	Split text into words
•	Remove punctuation and lowercase everything
•	Filter out stopwords (the, a, and, etc.)
•	Count word frequencies
I used pyspark.ml.feature.Tokenizer and CountVectorizer. The stopwords list I found online wasn't perfect - I had to manually add words like "food" and "place" to get meaningful results.
6. Positive vs Negative Words
I split the data based on rating (positive = >3 stars, negative = ≤3 stars) and repeated the word count. The difference was clear: positive reviews use words like "great" and "delicious", negative reviews use "bad" and "terrible".
7. Word Cloud & Association Graph
I exported the word frequencies to a CSV and used Python to generate the visualizations. The word cloud was easy; the association graph required building a co-occurrence matrix, which was computationally expensive.
8. Bigrams for Low-Star Reviews
I used NGram from PySpark ML to extract two-word phrases. I filtered for 1-2 star reviews and counted frequencies. "Cold food" and "rude staff" were the most common.
9. Review Length vs Rating
I calculated word count per review using split() and size():
python
review_df = review_df.withColumn("word_count", size(split(col("text"), " ")))
Then grouped by rating and averaged word count. The result showed 1-star reviews average 120 words, 5-star reviews average 70 words.
10. Mixed-Signal Reviews
I created a list of positive keywords (good, great, excellent, delicious, amazing, wonderful) and flagged reviews that had 1-2 stars but contained these words. I found about 12,000 mixed-signal reviews. Some were sarcastic, some were misclicks.
11. Chinese Restaurant Analysis
I first filtered businesses to only Chinese restaurants (using categories), then joined with reviews, then counted menu items from a food dictionary. The dictionary was tricky because "General Tso's" can be written in multiple ways.
________________________________________
Challenges I Faced
1.Performance: Running text analysis on 7 million reviews was slow. I learned to use .cache() and filter early when possible.
2.Stopwords: The standard stopwords list removed "good" and "bad" which I actually wanted. I had to customize it.
3.Bigrams: The NGram transformer created empty strings for short reviews. I had to filter out reviews with fewer than 2 words.
4.Mixed-Signal Detection: My simple keyword approach caught some false positives. For example, "not good" was counted as positive. I would need sentiment analysis to fix this.
________________________________________
Key Findings
1.Review volume peaked in 2015 with 4.2 million reviews, then declined.
2."Useful" votes (28.7 million) are much more common than "funny" (4.8 million) or "cool" (5.3 million).
3.Top 20 common words: good, food, great, service, place, etc.
4.Positive reviews use: great, excellent, delicious, amazing, friendly.
5.Negative reviews use: bad, service, terrible, rude, disappointed.
6.Most common pain points: "cold food", "rude staff", "long wait", "poor service".
7.1-star reviews average 120 words, 5-star reviews average 70 words.
8.12,847 mixed-signal reviews (1-2 stars with positive keywords) were found.
9.General Tso's Chicken is the most mentioned menu item in top Chinese restaurants.
________________________________________
What I Learned
This project taught me a lot about working with big data. PySpark is powerful but requires careful planning. Text analysis at scale is challenging because of the computational cost. I learned that simple approaches (like keyword matching) have limitations, but they can still reveal interesting patterns.
I also learned that reviews are not just ratings - they contain rich information about user behavior and business quality.
________________________________________
Visualizations
All charts are in the charts/review_analysis_charts/ folder:
1.Reviews Per Year
2.Useful, Funny, Cool Reviews
3.Top 5 Users Per Year
4.Top 20 Most Common Words
5.Top 10 Words - Positive Reviews
6.Top 10 Words - Negative Reviews
7.Word Cloud Analysis
8.Word Association Graph
9.Top 15 Bigrams
10.Review Length vs Rating
11.Mixed-Signal Reviews
12.Top 5 Chinese Restaurants
________________________________________
Code
All PySpark code is in the notebooks/ folder as Zeppelin notebooks. The queries are extracted to queries/ for easy reference.
________________________________________
Conclusion
This analysis showed that review patterns reveal a lot about user behavior. Satisfied customers write short praise; dissatisfied customers write long complaints. Review volume has declined since 2015. Text analysis can identify what customers like and what frustrates them.
________________________________________
Repository Link
https://github.com/Zaineb-Gharib/yelp-analysis-project04/tree/member3-Hajar-Choukri
