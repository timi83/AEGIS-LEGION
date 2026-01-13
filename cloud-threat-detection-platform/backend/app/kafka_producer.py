from kafka import KafkaProducer
import json
import os
import time

KAFKA_BROKER_URL = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

producer = None

def get_kafka_producer():
    global producer
    if producer is None:
        for _ in range(10):  # retry up to 10 times
            try:
                producer = KafkaProducer(
                    bootstrap_servers=[KAFKA_BROKER_URL],
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    retries=5
                )
                print("✔ Kafka Producer connected successfully")
                break
            except Exception as e:
                print("Waiting for Kafka...", str(e))
                time.sleep(3)
    return producer

def send_event(topic: str, payload: dict):
    prod = get_kafka_producer()
    prod.send(topic, payload)
    prod.flush()
