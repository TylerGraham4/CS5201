from flask import Flask, jsonify
from confluent_kafka import Consumer, KafkaException
import threading

app = Flask(__name__)

# Kafka Consumer Configuration
consumer_config = {
    'bootstrap.servers': 'kafka:9092',  # Ensure this matches the advertised Kafka broker in docker-compose.yml
    'group.id': 'admin_service',
    'auto.offset.reset': 'earliest'
}
consumer = Consumer(consumer_config)
consumer.subscribe(['pet_search_events'])  # Topic should match the one used in the Pet Search Service

# In-memory storage for consumed events
notifications = []

def consume_events():
    """Background thread to consume Kafka events."""
    global notifications
    while True:
        msg = consumer.poll(1.0)  # Poll Kafka for new events
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                continue
            else:
                print(f"Kafka error: {msg.error()}")
                break
        event = msg.value().decode('utf-8')
        notifications.append(event)
        print(f"Received event: {event}")

@app.route('/events', methods=['GET'])
def get_events():
    """Return all events consumed from Kafka."""
    global notifications
    return jsonify(notifications)

if __name__ == '__main__':
    # Start Kafka consumer in a background thread
    threading.Thread(target=consume_events, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=5003)
