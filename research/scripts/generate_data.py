import csv
import os

import psycopg2
import vertica_python
from clickhouse_driver import Client


def generate_data_and_create_tables():
    csv_path = "test_data.csv"
    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "value"])
            for i in range(1, 10000000):
                writer.writerow([i, f"Name_{i}", i * 10])
    create_vertica_table()
    create_clickhouse_table()
    create_postgres_table()


def create_vertica_table():
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
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS test_data (
        id INT PRIMARY KEY,
        name VARCHAR,
        value INT
    );
    """
    )
    conn.commit()
    conn.close()


def create_clickhouse_table():
    client = Client("localhost")
    client.execute(
        """
    CREATE TABLE IF NOT EXISTS test_data (
        id Int32,
        name String,
        value Int32
    ) ENGINE = MergeTree() 
    ORDER BY id;
    """
    )


def create_postgres_table():
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
        CREATE TABLE IF NOT EXISTS metrics (
            id SERIAL PRIMARY KEY, -- Используем SERIAL вместо AUTOINCREMENT
            transaction_type TEXT,
            batch_size INTEGER,
            time_taken REAL,
            cpu_time REAL,
            memory_usage REAL,
            db TEXT
        );
        """
    )
    conn.commit()
    cursor.close()
    conn.close()
