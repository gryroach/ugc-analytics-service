-- Таблица для чтения данных из Kafka
CREATE TABLE IF NOT EXISTS default.kafka_user_events (
    event_time DateTime,
    event_type String,
    user_id String,
    device_id String,
    device_type String,
    country String,
    region String,
    city String,
    session_id String,
    movie_id String,
    movie_title String,
    genre String,
    duration Int32,
    watch_time Int32,
    pause_time Int32,
    resume_time Int32,
    watch_duration Int32,
    rating Int32,
    search_query String,
    results_count Int32,
    registration_method String,
    login_method String
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka-0:9092',              -- Список брокеров Kafka
         kafka_topic_list = 'user_events',               -- Топик Kafka для чтения данных
         kafka_group_name = 'kafka_user_events_group',   -- Группа потребителей Kafka
         kafka_format = 'JSONEachRow',                   -- Формат данных в топике Kafka
         kafka_num_consumers = 1;                        -- Количество потребителей

-- Целевая таблица для хранения данных из Kafka
CREATE TABLE IF NOT EXISTS default.user_events (
    event_time DateTime,
    event_type String,
    user_id String,
    device_id String,
    device_type String,
    country String,
    region String,
    city String,
    session_id String,
    movie_id String,
    movie_title String,
    genre String,
    duration Int32,
    watch_time Int32,
    pause_time Int32,
    resume_time Int32,
    watch_duration Int32,
    rating Int32,
    search_query String,
    results_count Int32,
    registration_method String,
    login_method String
) ENGINE = MergeTree()
ORDER BY event_time;

-- Материализованное представление для записи данных из Kafka в целевую таблицу
CREATE MATERIALIZED VIEW IF NOT EXISTS default.kafka_to_user_events
TO default.user_events AS
SELECT 
    event_time,
    event_type,
    user_id,
    device_id,
    device_type,
    country,
    region,
    city,
    session_id,
    movie_id,
    movie_title,
    genre,
    duration,
    watch_time,
    pause_time,
    resume_time,
    watch_duration,
    rating,
    search_query,
    results_count,
    registration_method,
    login_method
FROM default.kafka_user_events;
