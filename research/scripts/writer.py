import threading
import time

import psycopg2
import vertica_python
from clickhouse_driver import Client


def run_aggregation_queries(database, num_threads, size, duration):
    threads = []

    for _ in range(num_threads):
        t = threading.Thread(
            target=aggregation_query_thread, args=(database, size, duration)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()


def aggregation_query_thread(database, size, duration):
    start_time = time.time()
    elapsed_time = 0
    while elapsed_time < duration:
        if database == "vertica":
            execute_vertica_query()
        elif database == "clickhouse":
            execute_clickhouse_query()
        elapsed_time = time.time() - start_time
        log_metrics("write", size, elapsed_time, database)


def execute_vertica_query():
    connection_info = {
        "host": "localhost",
        "port": 15433,
        "user": "dbadmin",
        "password": "password123",
        "database": "VMart",
        "read_timeout": 600,
        "write_timeout": 600,
        "connection_timeout": 10,
        "unicode_error": "strict",
        "ssl": False,
    }
    conn = vertica_python.connect(**connection_info)
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(value) FROM test_data")
    conn.close()


def execute_clickhouse_query():
    client = Client("localhost")
    client.execute("SELECT AVG(value) FROM test_data")


def log_metrics(transaction_type, batch_size, time_taken, db):
    conn = psycopg2.connect(
        dbname="metrics_db",
        user="user",
        password="password",
        host="localhost",
        port=5440,
    )
    cursor = conn.cursor()
    cursor.execute(
        """
    INSERT INTO metrics (transaction_type, batch_size, time_taken, db)
    VALUES (%s, %s, %s, %s)
    """,
        (transaction_type, batch_size, time_taken, db),
    )
    conn.commit()
    cursor.close()
    conn.close()
