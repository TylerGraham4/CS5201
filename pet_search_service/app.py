from flask import Flask, request, render_template_string
from confluent_kafka import Producer
import requests

app = Flask(__name__)

PETFINDER_API_KEY = "jHY0pnScj9SogAzR1rKKSFLqHCrSqOywuib7HaewzdTj8ZsLI4"
PETFINDER_API_SECRET = "A82kmUWeqG8EC3s9Z8xV0yY4gqS4qis24XeKMa5A"
PETFINDER_API_BASE_URL = "https://api.petfinder.com/v2"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Adoptable Pets</title>
</head>
<body>
    <h1>Adoptable Pets</h1>
    <ul>
        {% for animal in animals %}
        <li>
            <strong>Name:</strong> {{ animal['name'] }}<br>
            <strong>Breed:</strong> {{ animal['breed'] }}<br>
            <strong>Gender:</strong> {{ animal['gender'] }}<br>
            <strong>Age:</strong> {{ animal['age'] }}<br>
            <strong>Details:</strong> <a href="{{ animal['url'] }}" target="_blank">View Profile</a>
        </li>
        <hr>
        {% endfor %}
    </ul>
</body>
</html>
"""

# Kafka Producer Configuration
producer_config = {'bootstrap.servers': 'broker:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Delivery failed for record {msg.key()}: {err}")
    else:
        print(f"Record successfully produced to {msg.topic()} partition {msg.partition()} @ offset {msg.offset()}")

@app.route('/search', methods=['GET'])
def search_pets():
    params = {
        'location': request.args.get('location'),
        'breed': request.args.get('breed'),
        'type': request.args.get('type'),
        'age': request.args.get('age')
    }
    headers = {'Authorization': f'Bearer {get_petfinder_token()}'}
    response = requests.get(f"{PETFINDER_API_BASE_URL}/animals", params=params, headers=headers)
    pets = response.json().get('animals', [])

    # Process and extract relevant information
    processed_pets = [
        {
            'name': pet.get('name', 'Unknown'),
            'breed': f"{pet['breeds']['primary']} / {pet['breeds']['secondary']}" if pet['breeds']['secondary'] else pet['breeds']['primary'],
            'gender': pet.get('gender', 'Unknown'),
            'age': pet.get('age', 'Unknown'),
            'url': pet.get('url', '#')
        }
        for pet in pets
    ]

    # Produce Kafka events for the search
    event = {'event': 'pet_search', 'params': params, 'results': len(processed_pets)}
    producer.produce(
        topic='pet_search_events',
        key='search',
        value=str(event),
        callback=delivery_report
    )
    producer.flush()

    return render_template_string(HTML_TEMPLATE, animals=processed_pets)

def get_petfinder_token():
    response = requests.post(
        f"{PETFINDER_API_BASE_URL}/oauth2/token",
        data={'grant_type': 'client_credentials', 'client_id': PETFINDER_API_KEY, 'client_secret': PETFINDER_API_SECRET}
    )
    return response.json()['access_token']

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
