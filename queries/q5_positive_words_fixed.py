# Question 5: Top 10 Positive Sentiment Words (Fixed)
# Rating > 3

from pyspark.sql.functions import *
import matplotlib.pyplot as plt

stopwords = ['the', 'and', 'for', 'this', 'that', 'with', 'from', 'have', 
             'are', 'was', 'were', 'but', 'not', 'all', 'can', 'will', 
             'just', 'you', 'your', 'our', 'their', 'very', 'get', 'got']

neutral_words = ['they', 'had', 'there', 'out', 'when', 'would', 'like', 'here', 
                 'place', 'food', 'get', 'got', 'can', 'will', 'just', 'very',
                 'one', 'time', 'went', 'came', 'back', 'even', 'also', 'well']

expanded_stopwords = stopwords + neutral_words

positive_words = review_df.filter(col("stars") > 3) \
  .select(explode(split(regexp_replace(lower(col("text")), '[^a-zA-Z\\s]', ''), '\\s+')).alias("word")) \
  .filter((col("word") != "") & (length(col("word")) > 2)) \
  .filter(~col("word").isin(expanded_stopwords)) \
  .groupBy("word") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(10) \
  .toPandas()

print("="*60)
print("Top 10 Positive Sentiment Words (Rating > 3)")
print("="*60)
print(positive_words.to_string(index=False))
