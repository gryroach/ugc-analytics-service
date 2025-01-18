# Запуск всех контейнеров
run-all:
	docker compose up -d --build

# Запуск API получения событий
run-event-api:
	docker compose up -d --build nginx event-api

# Запуск Kafka
run-kafka:
	docker compose up -d --build kafka-init kafka-ui
