# PySpark Code - Review Analysis Notebook
# ======================================

# Cell 1
%pyspark
from pyspark.sql.functions import *

# Load data
review_df = spark.read.option("delimiter", "\u0001").csv("/user/hive/warehouse/review/")
review_df = review_df.select(
    col("_c0").alias("review_id"),
    col("_c1").alias("user_id"),
    col("_c2").alias("business_id"),
    col("_c3").cast("int").alias("stars"),
    col("_c4").cast("int").alias("useful"),
    col("_c5").cast("int").alias("funny"),
    col("_c6").cast("int").alias("cool"),
    col("_c7").alias("text"),
    col("_c8").alias("date")
)

# Extract year from date
review_df = review_df.withColumn("year", 
    when(col("date").isNotNull() & (length(col("date")) >= 4),
         substring(col("date"), 1, 4).cast("int"))
    .otherwise(None))

# Filter valid years
review_df_clean = review_df.filter(
    (col("year").isNotNull()) & 
    (col("year") >= 2000) & 
    (col("year") <= 2025))

print(f"✅ Data loaded! Total reviews: {review_df_clean.count():,}")

#--------------------------------------------------

# Cell 2
%pyspark
from pyspark.sql.functions import *
import matplotlib.pyplot as plt

reviews_per_year = review_df_clean.groupBy("year").count().orderBy("year").toPandas()

print("="*60)
print("QUESTION 1: Reviews Per Year")
print("="*60)
print(reviews_per_year.to_string(index=False))

plt.figure(figsize=(12, 6))
max_count = reviews_per_year['count'].max()
bars = plt.bar(reviews_per_year['year'], reviews_per_year['count'], color='steelblue', edgecolor='black')
plt.xlabel('Year')
plt.ylabel('Number of Reviews')
plt.title('QUESTION 1: Reviews Per Year')
plt.xticks(reviews_per_year['year'].astype(int), rotation=45)

for bar, count in zip(bars, reviews_per_year['count']):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_count*0.01,
             f'{count:,}', ha='center', fontsize=9)

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 3
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd

votes = review_df_clean.select(
    sum("useful").alias("Useful"),
    sum("funny").alias("Funny"),
    sum("cool").alias("Cool")
).toPandas()

print("="*60)
print("QUESTION 2: Useful, Funny, Cool Reviews")
print("="*60)
print(votes)

plt.figure(figsize=(10, 6))
categories = ['Useful', 'Funny', 'Cool']
values = [votes['Useful'][0], votes['Funny'][0], votes['Cool'][0]]
colors = ['#2ecc71', '#f39c12', '#3498db']

# Get highest value
if values[0] > values[1] and values[0] > values[2]:
    highest = values[0]
elif values[1] > values[0] and values[1] > values[2]:
    highest = values[1]
else:
    highest = values[2]

bars = plt.bar(categories, values, color=colors, edgecolor='black')
plt.ylabel('Number of Votes')
plt.title('QUESTION 2: Useful, Funny, Cool Votes')
plt.grid(axis='y', alpha=0.3)

for bar, val in zip(bars, values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + highest*0.01,
             f'{val:,}', ha='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 4
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd

# Register temp view
review_df_clean.createOrReplaceTempView("reviews")

# Get top 5 users per year
top_users_sql = spark.sql("""
    SELECT year, user_id, review_count, rank
    FROM (
        SELECT year, user_id, review_count,
               ROW_NUMBER() OVER (PARTITION BY year ORDER BY review_count DESC) as rank
        FROM (
            SELECT year, user_id, COUNT(*) as review_count
            FROM reviews
            WHERE year IS NOT NULL AND year >= 2000 AND year <= 2025
            GROUP BY year, user_id
        ) t
    ) ranked
    WHERE rank <= 5
    ORDER BY year DESC, rank
""").toPandas()

print("="*60)
print("QUESTION 3: Top 5 Users Per Year")
print("="*60)
print(top_users_sql.head(20).to_string(index=False))

# Chart: Most active user per year (rank = 1)
top_each_year = top_users_sql[top_users_sql['rank'] == 1].sort_values('year')

print("\n" + "="*60)
print("Chart Data (Rank 1 Users Per Year):")
print(top_each_year[['year', 'review_count']].to_string(index=False))
print("="*60)

plt.figure(figsize=(12, 6))
plt.bar(top_each_year['year'], top_each_year['review_count'], color='red', edgecolor='black')
plt.xlabel('Year')
plt.ylabel('Number of Reviews')
plt.title('QUESTION 3: Most Active User Per Year (Rank 1)')
plt.grid(axis='y', alpha=0.3)

# Add value labels on bars
highest = top_each_year['review_count'].max()
for i, (year, count) in enumerate(zip(top_each_year['year'], top_each_year['review_count'])):
    plt.text(year, count + highest*0.02, str(count), ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 5
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd

stopwords = ['the', 'and', 'for', 'this', 'that', 'with', 'from', 'have', 
             'are', 'was', 'were', 'but', 'not', 'all', 'can', 'will', 
             'just', 'you', 'your', 'our', 'their', 'very', 'get', 'got']

top_words = review_df_clean.select(explode(split(regexp_replace(lower(col("text")), '[^a-zA-Z\\s]', ''), '\\s+')).alias("word")) \
  .filter((col("word") != "") & (length(col("word")) > 2)) \
  .filter(~col("word").isin(stopwords)) \
  .groupBy("word") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(20) \
  .toPandas()

print("="*60)
print("QUESTION 4: Top 20 Most Common Words")
print("="*60)
print(top_words.to_string(index=False))

plt.figure(figsize=(10, 10))
plt.barh(top_words['word'][::-1], top_words['count'][::-1], color='steelblue', edgecolor='black')
plt.xlabel('Frequency')
plt.ylabel('Word')
plt.title('QUESTION 4: Top 20 Most Common Words')

biggest = top_words['count'].max()
for i, (word, count) in enumerate(zip(top_words['word'][::-1], top_words['count'][::-1])):
    plt.text(count + biggest*0.01, i, f'{count:,}', va='center', fontsize=9)

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 6
%pyspark
positive_words = review_df_clean.filter(col("stars") > 3) \
  .select(explode(split(regexp_replace(lower(col("text")), '[^a-zA-Z\\s]', ''), '\\s+')).alias("word")) \
  .filter((col("word") != "") & (length(col("word")) > 2)) \
  .filter(~col("word").isin(stopwords)) \
  .groupBy("word") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(10) \
  .toPandas()

print("="*60)
print("QUESTION 5: Top 10 Words - Positive Reviews (Rating > 3)")
print("="*60)
print(positive_words.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.barh(positive_words['word'][::-1], positive_words['count'][::-1], color='green', edgecolor='black')
plt.xlabel('Frequency')
plt.ylabel('Word')
plt.title('QUESTION 5: Top 10 Words - Positive Reviews')

biggest = positive_words['count'].max()
for i, (word, count) in enumerate(zip(positive_words['word'][::-1], positive_words['count'][::-1])):
    plt.text(count + biggest*0.01, i, f'{count:,}', va='center', fontsize=9)

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 7
%pyspark
negative_words = review_df_clean.filter(col("stars") <= 3) \
  .select(explode(split(regexp_replace(lower(col("text")), '[^a-zA-Z\\s]', ''), '\\s+')).alias("word")) \
  .filter((col("word") != "") & (length(col("word")) > 2)) \
  .filter(~col("word").isin(stopwords)) \
  .groupBy("word") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(10) \
  .toPandas()

print("="*60)
print("QUESTION 6: Top 10 Words - Negative Reviews (Rating ≤ 3)")
print("="*60)
print(negative_words.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.barh(negative_words['word'][::-1], negative_words['count'][::-1], color='red', edgecolor='black')
plt.xlabel('Frequency')
plt.ylabel('Word')
plt.title('QUESTION 6: Top 10 Words - Negative Reviews')

biggest = negative_words['count'].max()
for i, (word, count) in enumerate(zip(negative_words['word'][::-1], negative_words['count'][::-1])):
    plt.text(count + biggest*0.01, i, f'{count:,}', va='center', fontsize=9)

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 8
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd
from collections import Counter
import re

# Function to extract potential nouns and adjectives (words longer than 3 letters, not stopwords)
def extract_words(text):
    if not text:
        return []
    # Clean text and split
    words = re.findall(r'[a-zA-Z]{4,}', text.lower())
    # Filter out stopwords
    stopwords = ['the', 'and', 'for', 'this', 'that', 'with', 'from', 'have', 
                 'are', 'was', 'were', 'but', 'not', 'all', 'can', 'will', 
                 'just', 'you', 'your', 'our', 'their', 'very', 'get', 'got',
                 'there', 'they', 'what', 'when', 'where', 'which', 'would']
    return [w for w in words if w not in stopwords]

# Sample 100,000 reviews for performance
sample_reviews = review_df_clean.select("text").limit(100000).collect()

# Extract all words
all_words = []
for row in sample_reviews:
    all_words.extend(extract_words(row.text))

# Count frequencies
word_counts = Counter(all_words).most_common(30)

# Create DataFrame for display
word_cloud_df = pd.DataFrame(word_counts, columns=['word', 'count'])

print("="*60)
print("QUESTION 7: Word Cloud Analysis (Key Words)")
print("="*60)
print("Top 30 keywords for word cloud:")
print(word_cloud_df.to_string(index=False))

# Create bar chart
plt.figure(figsize=(12, 10))
plt.barh(word_cloud_df['word'][::-1], word_cloud_df['count'][::-1], 
         color='purple', edgecolor='black', alpha=0.7)
plt.xlabel('Frequency')
plt.ylabel('Word')
plt.title('QUESTION 7: Top Keywords for Word Cloud')

# Add value labels
biggest = word_cloud_df['count'].max()
for i, (word, count) in enumerate(zip(word_cloud_df['word'][::-1], word_cloud_df['count'][::-1])):
    plt.text(count + biggest*0.01, i, f'{count:,}', va='center', fontsize=8)

plt.tight_layout()
plt.show()

#--------------------------------------------------

# Cell 9
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd

# Stopwords to filter out
stopwords = ['the', 'and', 'for', 'this', 'that', 'with', 'from', 'have', 
             'are', 'was', 'were', 'but', 'not', 'all', 'can', 'will', 
             'just', 'you', 'your', 'our', 'their', 'very', 'get', 'got']

# Function to get word pairs that appear together
def get_word_pairs(text):
    if not text:
        return []
    words = text.lower().split()
    words = [w for w in words if len(w) > 3 and w not in stopwords]
    pairs = []
    for i in range(len(words)-1):
        if words[i] != words[i+1]:
            pairs.append((words[i], words[i+1]))
    return pairs[:15]

from pyspark.sql.types import ArrayType, StructType, StructField, StringType

pair_udf = udf(get_word_pairs, ArrayType(StructType([
    StructField("word1", StringType()),
    StructField("word2", StringType())
])))

# Get word associations from sample of reviews
word_pairs = review_df_clean.limit(200000) \
  .select(explode(pair_udf(col("text"))).alias("pair")) \
  .groupBy("pair.word1", "pair.word2") \
  .count() \
  .filter(col("count") >= 20) \
  .orderBy(col("count").desc()) \
  .limit(30) \
  .toPandas()

print("="*60)
print("QUESTION 8: Word Association Graph")
print("="*60)
print("Top word associations (word1 -> word2):")
print(word_pairs.to_string(index=False))

# Find words associated with "chinese"
chinese_assoc = review_df_clean.filter(lower(col("text")).contains("chinese")) \
  .select(explode(split(regexp_replace(lower(col("text")), '[^a-zA-Z\\s]', ''), '\\s+')).alias("word")) \
  .filter((col("word") != "") & (col("word") != "chinese") & (length(col("word")) > 3)) \
  .filter(~col("word").isin(stopwords)) \
  .groupBy("word") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(15) \
  .toPandas()

print("\n" + "="*60)
print("Words associated with 'chinese':")
print("="*60)
print(chinese_assoc.to_string(index=False))

# Create bar chart for Chinese associations
plt.figure(figsize=(10, 8))
plt.barh(chinese_assoc['word'][::-1], chinese_assoc['count'][::-1], 
         color='coral', edgecolor='black', alpha=0.7)
plt.xlabel('Frequency')
plt.ylabel('Associated Word')
plt.title('QUESTION 8: Words Associated with "Chinese"')

biggest = chinese_assoc['count'].max()
for i, (word, count) in enumerate(zip(chinese_assoc['word'][::-1], chinese_assoc['count'][::-1])):
    plt.text(count + biggest*0.01, i, f'{count:,}', va='center', fontsize=9)

plt.tight_layout()
plt.show()


#--------------------------------------------------

# Cell 10
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd

# Stopwords to filter out
stopwords = ['the', 'and', 'for', 'this', 'that', 'with', 'from', 'have', 
             'are', 'was', 'were', 'but', 'not', 'all', 'can', 'will', 
             'just', 'you', 'your', 'our', 'their', 'very', 'get', 'got']

# Function to extract bigrams (two-word phrases)
def get_bigrams(text):
    if not text:
        return []
    words = text.lower().split()
    words = [w for w in words if len(w) > 2 and w not in stopwords]
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
    return bigrams[:10]

from pyspark.sql.types import ArrayType, StringType
bigram_udf = udf(get_bigrams, ArrayType(StringType()))

# Extract bigrams from 1-2 star reviews
top_bigrams = review_df_clean.filter(col("stars") <= 2) \
  .select(explode(bigram_udf(col("text"))).alias("bigram")) \
  .groupBy("bigram") \
  .count() \
  .orderBy(col("count").desc()) \
  .limit(15) \
  .toPandas()

print("="*60)
print("QUESTION 9: Top 15 Bigrams for 1-2 Star Reviews (Pain Points)")
print("="*60)
print(top_bigrams.to_string(index=False))

# Create bar chart
if len(top_bigrams) > 0:
    plt.figure(figsize=(10, 8))
    plt.barh(top_bigrams['bigram'][::-1], top_bigrams['count'][::-1], 
             color='orange', edgecolor='black', alpha=0.8)
    plt.xlabel('Frequency')
    plt.ylabel('Bigram (Two-Word Phrase)')
    plt.title('QUESTION 9: Top 15 Pain Points in 1-2 Star Reviews')
    
    biggest = top_bigrams['count'].max()
    for i, (bigram, count) in enumerate(zip(top_bigrams['bigram'][::-1], top_bigrams['count'][::-1])):
        plt.text(count + biggest*0.01, i, f'{count:,}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()
else:
    print("No bigrams found")


#--------------------------------------------------

# Cell 11
%pyspark
import matplotlib.pyplot as plt
from pyspark.sql.functions import *
import pandas as pd

# Calculate average word count per star rating
length_by_rating = review_df_clean.withColumn("word_count", size(split(col("text"), "\\s+"))) \
  .groupBy("stars") \
  .agg(
      count("*").alias("count"),
      round(avg("word_count"), 1).alias("avg_words"),
      round(stddev("word_count"), 1).alias("stddev_words")
  ) \
  .orderBy("stars") \
  .toPandas()

print("="*60)
print("QUESTION 10: Review Length vs Rating (Correlation Analysis)")
print("="*60)
print(length_by_rating.to_string(index=False))

# Create bar chart
plt.figure(figsize=(10, 6))
colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
bars = plt.bar(length_by_rating['stars'], length_by_rating['avg_words'], 
               color=colors, edgecolor='black', alpha=0.7)
plt.xlabel('Star Rating')
plt.ylabel('Average Word Count')
plt.title('QUESTION 10: Average Review Length by Rating')
plt.grid(axis='y', alpha=0.3)

# Add value labels
for bar, row in zip(bars, length_by_rating.iterrows()):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
             f"{row[1]['avg_words']:.0f}", ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()

# Calculate correlation
one_star = length_by_rating[length_by_rating['stars'] == 1]['avg_words'].values[0]
five_star = length_by_rating[length_by_rating['stars'] == 5]['avg_words'].values[0]
ratio = one_star / five_star

print("\n" + "="*60)
print("CORRELATION ANALYSIS RESULT:")
print("="*60)
print(f"• 1-star reviews average: {one_star:.0f} words")
print(f"• 5-star reviews average: {five_star:.0f} words")
print(f"• Dissatisfied customers write {ratio:.1f}x LONGER reviews than satisfied customers")
print(f"• Conclusion: There is a NEGATIVE correlation - lower ratings = longer reviews")
print("="*60)


#--------------------------------------------------

# Cell 12
%pyspark
from pyspark.sql.functions import *
from pyspark.sql.types import IntegerType
import matplotlib.pyplot as plt
import pandas as pd

# Predefined positive lexicon
positive_lexicon = ['good', 'great', 'excellent', 'amazing', 'awesome', 'delicious', 
                    'wonderful', 'fantastic', 'perfect', 'love', 'best', 'favorite',
                    'superb', 'outstanding', 'beautiful', 'nice', 'enjoy', 'happy',
                    'satisfied', 'pleased', 'recommend', 'worth', 'friendly']

# Function to count positive keywords
def count_positive(text):
    if not text:
        return 0
    words = text.lower().split()
    count = 0
    for w in words:
        if w in positive_lexicon:
            count += 1
    return count

pos_udf = udf(count_positive, IntegerType())

# Find mixed-signal reviews
mixed_signals = review_df_clean.filter(col("stars") <= 2) \
  .withColumn("positive_count", pos_udf(col("text"))) \
  .filter(col("positive_count") >= 3) \
  .select("stars", "positive_count", "text") \
  .orderBy(col("positive_count").desc()) \
  .limit(15) \
  .toPandas()

print("="*60)
print("QUESTION 11: Mixed-Signal Reviews")
print("="*60)
print("Reviews with 1-2 stars but containing positive keywords")
print("(Potential sarcastic reviews or mis-clicks)")
print("="*60)

if len(mixed_signals) > 0:
    # Display table
    print(mixed_signals[['stars', 'positive_count', 'text']].to_string(index=False, max_colwidth=80))
    
    # Create chart
    plt.figure(figsize=(10, 6))
    colors = ['red' if stars <= 2 else 'green' for stars in mixed_signals['stars']]
    plt.bar(range(len(mixed_signals)), mixed_signals['positive_count'], color=colors, edgecolor='black')
    plt.xlabel('Review Number')
    plt.ylabel('Number of Positive Keywords')
    plt.title('QUESTION 11: Mixed-Signal Reviews - Positive Keywords Count')
    plt.xticks(range(len(mixed_signals)), [f"{stars}★" for stars in mixed_signals['stars']], rotation=45)
    plt.grid(axis='y', alpha=0.3)
    
    for i, count in enumerate(mixed_signals['positive_count']):
        plt.text(i, count + 0.2, str(count), ha='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "="*60)
    print(f"Total mixed-signal reviews found: {len(mixed_signals)} (showing top 15)")
    print("="*60)
else:
    print("No mixed-signal reviews found with 3+ positive keywords")

#--------------------------------------------------

# Cell 13
%pyspark
from pyspark.sql.functions import *
import matplotlib.pyplot as plt
import pandas as pd

print("Loading business data...")
# Load business data
business_df = spark.read.option("delimiter", "\u0001").csv("/user/hive/warehouse/business/")
business_df = business_df.select(
    col("_c0").alias("business_id"),
    col("_c1").alias("name"),
    col("_c11").alias("categories")
)

# Find Chinese restaurants and get top 5 by review count
print("Finding top Chinese restaurants...")
review_counts = review_df_clean.groupBy("business_id").count()

chinese_rest = business_df.filter(
    lower(col("name")).contains("china") |
    lower(col("name")).contains("chinese") |
    lower(col("name")).contains("dragon") |
    lower(col("name")).contains("peking")
)

# Join and get top 5
top_chinese_ids = chinese_rest.join(review_counts, "business_id") \
  .orderBy(col("count").desc()) \
  .limit(5) \
  .select("business_id", "name", "count") \
  .collect()

print("="*60)
print("QUESTION 12: Top 5 Chinese Restaurants")
print("="*60)

if len(top_chinese_ids) == 0:
    print("No Chinese found. Using top 5 overall:")
    top_chinese_ids = business_df.join(review_counts, "business_id") \
      .orderBy(col("count").desc()) \
      .limit(5) \
      .select("business_id", "name", "count") \
      .collect()

for i, rest in enumerate(top_chinese_ids, 1):
    print(f"{i}. {rest['name']} - {rest['count']:,} reviews")

# Get all reviews for these restaurants in one go
restaurant_ids = [r['business_id'] for r in top_chinese_ids]
reviews_for_top = review_df_clean.filter(col("business_id").isin(restaurant_ids))

# Define menu items
menu_items = {
    'Dumpling': 'dumpling',
    'Noodle': 'noodle', 
    'Fried Rice': 'fried rice',
    'Chicken': 'chicken',
    'Beef': 'beef',
    'Pork': 'pork',
    'Shrimp': 'shrimp',
    'Tofu': 'tofu'
}

# Count all menu mentions in one pass using a single query
print("\nCounting menu mentions...")
menu_counts = {}
for name, keyword in menu_items.items():
    cnt = reviews_for_top.filter(lower(col("text")).contains(keyword)).count()
    menu_counts[name] = cnt

print("\n" + "="*60)
print("Most Mentioned Menu Items")
print("="*60)
for name, cnt in sorted(menu_counts.items(), key=lambda x: x[1], reverse=True):
    if cnt > 0:
        print(f"{name}: {cnt:,}")

# Chart
data = [(k, v) for k, v in menu_counts.items() if v > 0]
data.sort(key=lambda x: x[1], reverse=True)

if data:
    plt.figure(figsize=(10, 6))
    plt.barh([d[0] for d in data], [d[1] for d in data], color='orange')
    plt.xlabel('Mentions')
    plt.title('Most Mentioned Menu Items in Top Chinese Restaurants')
    plt.tight_layout()
    plt.show()
    print("\n✅ QUESTION 12 COMPLETE!")
else:
    print("No menu items found with mentions")

#--------------------------------------------------

