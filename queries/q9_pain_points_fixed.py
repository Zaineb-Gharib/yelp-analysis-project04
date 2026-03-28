# Question 9: Top 15 Pain Point Bigrams (Fixed)
# 1-2 Star Reviews

from pyspark.sql.functions import *
from pyspark.sql.types import ArrayType, StringType

stopwords_bigrams = ['the', 'and', 'for', 'this', 'that', 'with', 'from', 'have', 
                     'are', 'was', 'were', 'but', 'not', 'all', 'can', 'will', 
                     'just', 'you', 'your', 'our', 'their', 'very', 'get', 'got',
                     'they', 'had', 'there', 'out', 'when', 'would', 'like', 'here', 
                     'place', 'food', 'one', 'time', 'went', 'came', 'back', 'even', 
                     'also', 'well', 'ive', 'been', 'could', 'give', 'has', 'last',
                     'first', 'ever', 'night', 'star']

def get_pain_point_bigrams(text):
    if not text:
        return []
    words = text.lower().split()
    words = [''.join(c for c in w if c.isalpha()) for w in words]
    words = [w for w in words if len(w) > 2 and w not in stopwords_bigrams]
    
    bigrams = []
    for i in range(len(words)-1):
        bigram = f"{words[i]} {words[i+1]}"
        pain_indicators = ['cold', 'rude', 'slow', 'bad', 'terrible', 'awful', 
                          'horrible', 'disappointing', 'worst', 'poor', 'wrong',
                          'overpriced', 'dirty', 'small', 'long', 'wait', 'service',
                          'manager', 'staff', 'order', 'mistake', 'problem']
        if any(indicator in bigram for indicator in pain_indicators):
            bigrams.append(bigram)
    return bigrams[:20]

pain_bigram_udf = udf(get_pain_point_bigrams, ArrayType(StringType()))

top_bigrams = review_df.filter(col("stars") <= 2) \
  .select(explode(pain_bigram_udf(col("text"))).alias("bigram")) \
  .groupBy("bigram") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(15) \
  .toPandas()

print("="*60)
print("Top 15 Pain Point Bigrams (1-2 Star Reviews)")
print("="*60)
print(top_bigrams.to_string(index=False))
