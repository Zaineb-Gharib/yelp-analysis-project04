-- business
;

-- checkin
;

-- checkin_daily_city_tbl
;

-- checkin_weather_tbl
;

-- json_business
;

-- json_checkin
;

-- json_review
;

-- json_tip
;

-- json_user
;

-- review
;

-- reviews_small_tbl
;

-- tip
;

-- users
;

-- weather
;

-- weather_final_tbl
;

-- business
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `business`(                  |
|   `business_id` string,                            |
|   `name` string,                                   |
|   `address` string,                                |
|   `city` string,                                   |
|   `state` string,                                  |
|   `postal_code` string,                            |
|   `latitude` float,                                |
|   `longitude` float,                               |
|   `stars` float,                                   |
|   `review_count` int,                              |
|   `is_open` tinyint,                               |
|   `attributes` string,                             |
|   `categories` string,                             |
|   `hours` string)                                  |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/business' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'bucketing_version'='2',                         |
|   'external.table.purge'='TRUE',                   |
|   'transient_lastDdlTime'='1774237750')            |
+----------------------------------------------------+
;

-- checkin
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `checkin`(                   |
|   `business_id` string,                            |
|   `checkin_dates` string)                          |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/checkin' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'bucketing_version'='2',                         |
|   'external.table.purge'='TRUE',                   |
|   'transient_lastDdlTime'='1774244072')            |
+----------------------------------------------------+
;

-- checkin_daily_city_tbl
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `checkin_daily_city_tbl`(    |
|   `city` string,                                   |
|   `date` date,                                     |
|   `daily_checkin_count` bigint)                    |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'  |
| WITH SERDEPROPERTIES (                             |
|   'path'='hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/checkin_daily_city_tbl')  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'  |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/checkin_daily_city_tbl' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'external.table.purge'='TRUE',                   |
|   'spark.sql.create.version'='3.5.1',              |
|   'spark.sql.sources.provider'='parquet',          |
|   'spark.sql.sources.schema'='{"type":"struct","fields":[{"name":"city","type":"string","nullable":true,"metadata":{}},{"name":"date","type":"date","nullable":true,"metadata":{}},{"name":"daily_checkin_count","type":"long","nullable":true,"metadata":{}}]}',  |
|   'transient_lastDdlTime'='1774449171')            |
+----------------------------------------------------+
;

-- checkin_weather_tbl
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `checkin_weather_tbl`(       |
|   `city` string,                                   |
|   `date` date,                                     |
|   `daily_checkin_count` bigint,                    |
|   `precip_in` double,                              |
|   `temp_max_f` int,                                |
|   `temp_min_f` int,                                |
|   `wind_mph` double,                               |
|   `rain_flag` int,                                 |
|   `heavy_rain_flag` int,                           |
|   `strong_wind_flag` int,                          |
|   `extreme_heat_flag` int)                         |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'  |
| WITH SERDEPROPERTIES (                             |
|   'path'='hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/checkin_weather_tbl')  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'  |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/checkin_weather_tbl' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'external.table.purge'='TRUE',                   |
|   'spark.sql.create.version'='3.5.1',              |
|   'spark.sql.sources.provider'='parquet',          |
|   'spark.sql.sources.schema'='{"type":"struct","fields":[{"name":"city","type":"string","nullable":true,"metadata":{}},{"name":"date","type":"date","nullable":true,"metadata":{}},{"name":"daily_checkin_count","type":"long","nullable":true,"metadata":{}},{"name":"precip_in","type":"double","nullable":true,"metadata":{}},{"name":"temp_max_f","type":"integer","nullable":true,"metadata":{}},{"name":"temp_min_f","type":"integer","nullable":true,"metadata":{}},{"name":"wind_mph","type":"double","nullable":true,"metadata":{}},{"name":"rain_flag","type":"integer","nullable":true,"metadata":{}},{"name":"heavy_rain_flag","type":"integer","nullable":true,"metadata":{}},{"name":"strong_wind_flag","type":"integer","nullable":true,"metadata":{}},{"name":"extreme_heat_flag","type":"integer","nullable":true,"metadata":{}}]}',  |
|   'transient_lastDdlTime'='1774449724')            |
+----------------------------------------------------+
;

-- json_business
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `json_business`(             |
|   `json_body` string)                              |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/root/yelp/business'  |
| TBLPROPERTIES (                                    |
|   'bucketing_version'='2',                         |
|   'transient_lastDdlTime'='1774237621')            |
+----------------------------------------------------+
;

-- json_checkin
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `json_checkin`(              |
|   `json_body` string)                              |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/root/yelp/checkin'   |
| TBLPROPERTIES (                                    |
|   'bucketing_version'='2',                         |
|   'transient_lastDdlTime'='1774243930')            |
+----------------------------------------------------+
;

-- json_review
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `json_review`(               |
|   `json_body` string)                              |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/root/yelp/review'    |
| TBLPROPERTIES (                                    |
|   'bucketing_version'='2',                         |
|   'transient_lastDdlTime'='1774242091')            |
+----------------------------------------------------+
;

-- json_tip
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `json_tip`(                  |
|   `json_body` string)                              |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/root/yelp/tip'       |
| TBLPROPERTIES (                                    |
|   'bucketing_version'='2',                         |
|   'transient_lastDdlTime'='1774244402')            |
+----------------------------------------------------+
;

-- json_user
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `json_user`(                 |
|   `json_body` string)                              |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/root/yelp/user'      |
| TBLPROPERTIES (                                    |
|   'bucketing_version'='2',                         |
|   'transient_lastDdlTime'='1774243110')            |
+----------------------------------------------------+
;

-- review
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `review`(                    |
|   `review_id` string,                              |
|   `rev_user_id` string,                            |
|   `rev_business_id` string,                        |
|   `rev_stars` int,                                 |
|   `rev_useful` int,                                |
|   `rev_funny` int,                                 |
|   `rev_cool` int,                                  |
|   `rev_text` string,                               |
|   `rev_timestamp` string,                          |
|   `rev_date` date)                                 |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/review' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'bucketing_version'='2',                         |
|   'external.table.purge'='TRUE',                   |
|   'transient_lastDdlTime'='1774242328')            |
+----------------------------------------------------+
;

-- reviews_small_tbl
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `reviews_small_tbl`(         |
|   `business_id` string,                            |
|   `stars` int,                                     |
|   `date` date,                                     |
|   `city` string)                                   |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'  |
| WITH SERDEPROPERTIES (                             |
|   'path'='hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/reviews_small_tbl')  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'  |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/reviews_small_tbl' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'external.table.purge'='TRUE',                   |
|   'spark.sql.create.version'='3.5.1',              |
|   'spark.sql.sources.provider'='parquet',          |
|   'spark.sql.sources.schema'='{"type":"struct","fields":[{"name":"business_id","type":"string","nullable":true,"metadata":{}},{"name":"stars","type":"integer","nullable":true,"metadata":{}},{"name":"date","type":"date","nullable":true,"metadata":{}},{"name":"city","type":"string","nullable":true,"metadata":{}}]}',  |
|   'transient_lastDdlTime'='1774433646')            |
+----------------------------------------------------+
;

-- tip
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `tip`(                       |
|   `text` string,                                   |
|   `date` string,                                   |
|   `compliment_count` int,                          |
|   `business_id` string,                            |
|   `user_id` string)                                |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/tip' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'bucketing_version'='2',                         |
|   'external.table.purge'='TRUE',                   |
|   'transient_lastDdlTime'='1774244698')            |
+----------------------------------------------------+
;

-- users
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `users`(                     |
|   `user_id` string,                                |
|   `user_name` string,                              |
|   `user_review_count` int,                         |
|   `user_yelping_since` string,                     |
|   `user_friends` string,                           |
|   `user_useful` int,                               |
|   `user_funny` int,                                |
|   `user_cool` int,                                 |
|   `user_fans` int,                                 |
|   `user_elite` string,                             |
|   `user_average_stars` float,                      |
|   `user_compliment_hot` int,                       |
|   `user_compliment_more` int,                      |
|   `user_compliment_profile` int,                   |
|   `user_compliment_cute` int,                      |
|   `user_compliment_list` int,                      |
|   `user_compliment_note` int,                      |
|   `user_compliment_plain` int,                     |
|   `user_compliment_cool` int,                      |
|   `user_compliment_funny` int,                     |
|   `user_compliment_writer` int,                    |
|   `user_compliment_photos` int)                    |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/users' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'bucketing_version'='2',                         |
|   'external.table.purge'='TRUE',                   |
|   'transient_lastDdlTime'='1774243553')            |
+----------------------------------------------------+
;

-- weather
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `weather`(                   |
|   `station_id` string,                             |
|   `date` string,                                   |
|   `prcp` double,                                   |
|   `tavg` double,                                   |
|   `tmax` double,                                   |
|   `tmin` double,                                   |
|   `awnd` double)                                   |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'  |
| WITH SERDEPROPERTIES (                             |
|   'field.delim'=',',                               |
|   'serialization.format'=',')                      |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.mapred.TextInputFormat'       |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/weather' |
| TBLPROPERTIES (                                    |
|   'spark.sql.create.version'='3.5.1',              |
|   'spark.sql.sources.schema'='{"type":"struct","fields":[{"name":"station_id","type":"string","nullable":true,"metadata":{}},{"name":"date","type":"string","nullable":true,"metadata":{}},{"name":"prcp","type":"double","nullable":true,"metadata":{}},{"name":"tavg","type":"double","nullable":true,"metadata":{}},{"name":"tmax","type":"double","nullable":true,"metadata":{}},{"name":"tmin","type":"double","nullable":true,"metadata":{}},{"name":"awnd","type":"double","nullable":true,"metadata":{}}]}',  |
|   'transient_lastDdlTime'='1774407997')            |
+----------------------------------------------------+
;

-- weather_final_tbl
+----------------------------------------------------+
|                   createtab_stmt                   |
+----------------------------------------------------+
| CREATE EXTERNAL TABLE `weather_final_tbl`(         |
|   `city` string,                                   |
|   `date` date,                                     |
|   `precip_in` double,                              |
|   `temp_max_f` int,                                |
|   `temp_min_f` int,                                |
|   `wind_mph` double,                               |
|   `rain_flag` int,                                 |
|   `heavy_rain_flag` int,                           |
|   `strong_wind_flag` int,                          |
|   `extreme_heat_flag` int)                         |
| ROW FORMAT SERDE                                   |
|   'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'  |
| WITH SERDEPROPERTIES (                             |
|   'path'='hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/weather_final_tbl')  |
| STORED AS INPUTFORMAT                              |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'  |
| OUTPUTFORMAT                                       |
|   'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat' |
| LOCATION                                           |
|   'hdfs://localhost:9000/user/hive/warehouse/yelp_db.db/weather_final_tbl' |
| TBLPROPERTIES (                                    |
|   'TRANSLATED_TO_EXTERNAL'='TRUE',                 |
|   'external.table.purge'='TRUE',                   |
|   'spark.sql.create.version'='3.5.1',              |
|   'spark.sql.sources.provider'='parquet',          |
|   'spark.sql.sources.schema'='{"type":"struct","fields":[{"name":"city","type":"string","nullable":true,"metadata":{}},{"name":"date","type":"date","nullable":true,"metadata":{}},{"name":"precip_in","type":"double","nullable":true,"metadata":{}},{"name":"temp_max_f","type":"integer","nullable":true,"metadata":{}},{"name":"temp_min_f","type":"integer","nullable":true,"metadata":{}},{"name":"wind_mph","type":"double","nullable":true,"metadata":{}},{"name":"rain_flag","type":"integer","nullable":true,"metadata":{}},{"name":"heavy_rain_flag","type":"integer","nullable":true,"metadata":{}},{"name":"strong_wind_flag","type":"integer","nullable":true,"metadata":{}},{"name":"extreme_heat_flag","type":"integer","nullable":true,"metadata":{}}]}',  |
|   'transient_lastDdlTime'='1774433490')            |
+----------------------------------------------------+
;

