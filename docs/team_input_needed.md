# What I Need From You to Build the Backend

## 1. All Tables in Hive

Please list ALL tables that exist in our Hive database:

| Table Name | Purpose | Key Columns |
|------------|---------|-------------|
| business | Business info | name, city, stars, categories |
| review | Reviews | stars, text, date |
| users | User info | name, review_count, fans, elite |
| checkin | Check-ins | business_id, date |
| tip | Tips | user_id, business_id, text |
| *(add any new tables here)* | | |

---

## 2. Enrichment Tables (If Created)

Did anyone create tables for these tracks?

| Track | Member | Table Name? | If YES, list columns |
|-------|--------|-------------|---------------------|
| Weather-Mood | Member 1 | | |
| Cursed Storefronts | Member 3 | | |
| Review Manipulation | Member 3 | | |
| Open-World Safari | Member 4 | | |

---

## 3. LLM API Key

Who can get an API key for AI to generate SQL?

| Option | Cost |
|--------|------|
| DeepSeek | ~$0.14 per 1M tokens |
| OpenAI | ~$2.50 per 1M tokens |
| Ollama | Free (local) |

**Who will set this up?** ______________

---

## 4. Testing

When frontend is ready, let me know so we can test.

---

Thanks!
