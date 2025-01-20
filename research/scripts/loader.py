import threading
import time

import psycopg2
import vertica_python
from clickhouse_driver import Client


def load_data(database, batch_size, num_threads, duration):
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(
            target=load_thread, args=(database, batch_size, duration)
        )
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def load_thread(database, batch_size, duration):
    start_time = time.time()
    elapsed_time = 0
    while elapsed_time < duration:
        batch = generate_batch(batch_size)
        if database == "vertica":
            load_vertica(batch)
        elif database == "clickhouse":
            load_clickhouse(batch)
        elapsed_time = time.time() - start_time
        log_metrics("read", batch_size, elapsed_time, database)


def generate_batch(batch_size):
    return [(i, f"Name_{i}", i * 10) for i in range(batch_size)]


def load_vertica(batch):
    connection_info = {
        "host": "localhost",
        "port": 15433,
        "user": "dbadmin",
        "password": "password123",
        "database": "VMart",
        "read_timeout": 10,
        "write_timeout": 10,
        "connection_timeout": 10,
        "unicode_error": "strict",
        "ssl": False,
    }
    conn = vertica_python.connect(**connection_info)
    cursor = conn.cursor()
    cursor.executemany(
        """
    INSERT INTO test_data (id, name, value) VALUES (%s, %s, %s)
    """,
        batch,
    )
    conn.commit()
    conn.close()


def load_clickhouse(batch):
    client = Client("localhost")
    client.execute(
        """
    INSERT INTO test_data (id, name, value) VALUES
    """,
        batch,
    )


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
