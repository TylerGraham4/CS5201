from flask import Flask, request, jsonify
from confluent_kafka import Producer

app = Flask(__name__)

# In-memory database for simplicity
users = {}

# Kafka Producer
producer_config = {'bootstrap.servers': 'broker:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record successfully produced to {msg.topic()} partition {msg.partition()} @ offset {msg.offset()}")

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({'message': 'Email is required'}), 400
    if data['email'] in users:
        return jsonify({'message': 'User already exists'}), 400
    
    users[data['email']] = {'favorites': []}
    return jsonify({'message': 'User registered successfully'})

@app.route('/favorites/<email>', methods=['POST'])
def add_favorite(email):
    if email not in users:
        return jsonify({'message': 'User not found'}), 404

    pet_id = request.json.get('pet_id')
    if not pet_id:
        return jsonify({'message': 'Pet ID is required'}), 400
    
    users[email]['favorites'].append(pet_id)

    # Produce an event to Kafka
    event = {'user': email, 'pet_id': pet_id, 'event': 'added_to_favorites'}
    producer.produce(
        topic='favorite_pet_events',
        key=email,
        value=str(event),
        callback=delivery_report
    )
    producer.flush()

    return jsonify({'message': f'Pet {pet_id} added to favorites'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
