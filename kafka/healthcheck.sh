#!/bin/sh

# Check if Kafka is ready
kafka-topics.sh --list --bootstrap-server localhost:9092 > /dev/null 2>&1
