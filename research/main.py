import base64
import threading
import time
from io import BytesIO

import matplotlib.pyplot as plt
import psycopg2

from scripts.generate_data import create_tables
from scripts.loader import load_data
from scripts.writer import run_aggregation_queries


def main(duration, workers, batches):
    create_tables()
    for size in batches:
        # Vertica
        threading.Thread(
            target=load_data, args=("vertica", size, workers, duration)
        ).start()
        threading.Thread(
            target=run_aggregation_queries,
            args=("vertica", workers, size, duration),
        ).start()
        # Ожидание завершения всех потоков
        time.sleep(duration + 1)
        # Clickhouse
        threading.Thread(
            target=load_data, args=("clickhouse", size, workers, duration)
        ).start()
        threading.Thread(
            target=run_aggregation_queries,
            args=("clickhouse", workers, size, duration),
        ).start()
        # Ожидание завершения всех потоков
        time.sleep(duration + 1)
    generate_report(workers)


def generate_report(workers):
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
        SELECT 
            db,
            transaction_type, 
            batch_size, 
            AVG(time_taken) AS avg_time_taken
        FROM metrics
        WHERE transaction_type = 'read'
        GROUP BY transaction_type, batch_size, db
        ORDER BY db, transaction_type, batch_size;
    """
    )
    data = cursor.fetchall()
    report = "# Аналитический отчет {} воркеров (read/write) \n\n".format(
        workers * 2
    )
    report += "| Database | Transaction Type | Batch Size | Avg Time Taken |\n"
    report += "|----------|------------------|------------|----------------|\n"
    db_data = {}
    for row in data:
        database, transaction_type, batch_size, avg_time_taken = row
        report += f"| {database} | {transaction_type} | {batch_size} | {avg_time_taken} |\n"
        if database not in db_data:
            db_data[database] = {"batch_sizes": [], "avg_times": []}
        db_data[database]["batch_sizes"].append(batch_size)
        db_data[database]["avg_times"].append(avg_time_taken)
    plt.figure(figsize=(10, 6))
    for database, values in db_data.items():
        plt.plot(
            values["batch_sizes"],
            values["avg_times"],
            marker="o",
            label=database,
        )
    plt.xlabel("Batch Size")
    plt.ylabel("Avg Time Taken (s)")
    plt.title(f"Avg Time Taken vs Batch Size (Read Transactions)")
    plt.grid(True)
    plt.legend(title="Database")
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.read()).decode("utf-8")
    report += (
        "\n### График зависимости времени чтения"
        " от размера batch при параллельной операции записи"
        "\n![Avg Time Taken vs Batch Size (Read Transactions)]"
        f"(data:image/png;base64,{img_base64})\n"
    )
    with open("report.md", "w") as f:
        f.write(report)
    print("Отчёт успешно сгенерирован и сохранён в 'report.md'.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    main(
        duration=3,
        workers=8,
        batches=(
            1000,
            5000,
            10000,
            25000,
            50000,
            75000,
            100000,
            150000,
            200000,
        ),
    )
