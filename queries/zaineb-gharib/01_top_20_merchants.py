
# QUESTION 1: Top 20 Most Common Merchants

result = spark.sql("""
SELECT name, COUNT(*) as location_count
FROM business
GROUP BY name
ORDER BY location_count DESC
LIMIT 20
""")

result.show()
