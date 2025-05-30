-- Таблица для чтения данных из Kafka
CREATE TABLE IF NOT EXISTS default.kafka_user_events (
    event_time DateTime64,
    event_type String,
    user_id Nullable(String),
    user_role Nullable(String),
    user_verified Bool,
    ip_address Nullable(String),
    browser Nullable(String),
    operating_system Nullable(String),
    timestamp DateTime64,
    device_id Nullable(String),
    device_type Nullable(String),
    country Nullable(String),
    region Nullable(String),
    city Nullable(String),
    session_id Nullable(String),
    session_start_time Nullable(DateTime64),
    session_end_time Nullable(DateTime64),
    movie_id Nullable(String),
    movie_title Nullable(String),
    genre Nullable(String),
    duration Nullable(Int32),
    watch_time Nullable(Int32),
    pause_time Nullable(Int32),
    resume_time Nullable(Int32),
    watch_duration Nullable(Int32),
    rating Nullable(Int32),
    search_query Nullable(String),
    results_count Nullable(Int32),
    registration_method Nullable(String),
    login_method Nullable(String),
    email Nullable(String),
    comment_text Nullable(String),
    trailer_duration Nullable(Int32)
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka-0:9092',             -- Список брокеров Kafka
         kafka_topic_list = 'user_events',               -- Топик Kafka для чтения данных
         kafka_group_name = 'kafka_user_events_group',   -- Группа потребителей Kafka
         kafka_format = 'JSONEachRow',                   -- Формат данных в топике Kafka
         kafka_num_consumers = 1;                        -- Количество потребителей

-- Целевая таблица для хранения данных из Kafka
CREATE TABLE IF NOT EXISTS default.user_events (
    event_time DateTime64,
    event_type String,
    user_id Nullable(String),
    user_role Nullable(String),
    user_verified Bool,
    ip_address Nullable(String),
    browser Nullable(String),
    operating_system Nullable(String),
    timestamp DateTime64,
    device_id Nullable(String),
    device_type Nullable(String),
    country Nullable(String),
    region Nullable(String),
    city Nullable(String),
    session_id Nullable(String),
    session_start_time Nullable(DateTime64),
    session_end_time Nullable(DateTime64),
    movie_id Nullable(String),
    movie_title Nullable(String),
    genre Nullable(String),
    duration Nullable(Int32),
    watch_time Nullable(Int32),
    pause_time Nullable(Int32),
    resume_time Nullable(Int32),
    watch_duration Nullable(Int32),
    rating Nullable(Int32),
    search_query Nullable(String),
    results_count Nullable(Int32),
    registration_method Nullable(String),
    login_method Nullable(String),
    email Nullable(String),
    comment_text Nullable(String),
    trailer_duration Nullable(Int32)
) ENGINE = MergeTree()
ORDER BY event_time;

-- Материализованное представление для записи данных из Kafka в целевую таблицу
CREATE MATERIALIZED VIEW IF NOT EXISTS default.kafka_to_user_events
TO default.user_events AS
SELECT 
    event_time,
    event_type,
    user_id,
    user_role,
    user_verified,
    ip_address,
    browser,
    operating_system,
    timestamp,
    device_id,
    device_type,
    country,
    region,
    city,
    session_id,
    session_start_time,
    session_end_time,
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
    login_method,
    email,
    comment_text,
    trailer_duration
FROM default.kafka_user_events;
