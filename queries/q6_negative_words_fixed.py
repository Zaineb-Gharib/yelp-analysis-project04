# Question 6: Top 10 Negative Sentiment Words (Fixed)
# Rating ≤ 3

from pyspark.sql.functions import *

negative_sentiment_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 
                            'worst', 'poor', 'rude', 'slow', 'cold', 'dirty', 
                            'overpriced', 'expensive', 'small', 'long', 'wait', 
                            'mistake', 'wrong', 'problem', 'unfriendly', 'disappointed',
                            'horrendous', 'atrocious', 'mediocre', 'underwhelming',
                            'subpar', 'disgusting', 'nasty', 'gross', 'burnt', 'bland']

negative_words = review_df.filter(col("stars") <= 3) \
  .select(explode(split(regexp_replace(lower(col("text")), '[^a-zA-Z\\s]', ''), '\\s+')).alias("word")) \
  .filter(col("word").isin(negative_sentiment_words)) \
  .groupBy("word") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(10) \
  .toPandas()

print("="*60)
print("Top 10 Negative Sentiment Words (Rating ≤ 3)")
print("="*60)
print(negative_words.to_string(index=False))
