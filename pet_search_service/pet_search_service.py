from flask import Flask, request, render_template, jsonify, redirect
import requests

app = Flask(__name__)

PETFINDER_API_KEY = "jHY0pnScj9SogAzR1rKKSFLqHCrSqOywuib7HaewzdTj8ZsLI4"
PETFINDER_API_SECRET = "A82kmUWeqG8EC3s9Z8xV0yY4gqS4qis24XeKMa5A"
PETFINDER_API_BASE_URL = "https://api.petfinder.com/v2"

@app.route('/')
def search_menu():
    """Serve the search menu form."""
    return render_template("search_menu.html")

@app.route('/search', methods=['GET'])
def search_pets():
    """Search for pets and render results."""
    params = {key: value for key, value in request.args.items() if value}
    params['limit'] = 5  # Restrict results to 5 pets

    headers = {'Authorization': f'Bearer {get_petfinder_token()}'}
    response = requests.get(f"{PETFINDER_API_BASE_URL}/animals", params=params, headers=headers)
    pets = response.json().get('animals', [])

    processed_pets = [
        {
            'id': pet.get('id', 'Unknown'),
            'name': pet.get('name', 'Unknown'),
            'breed': f"{pet['breeds']['primary']} / {pet['breeds']['secondary']}" if pet['breeds']['secondary'] else pet['breeds']['primary'],
            'gender': pet.get('gender', 'Unknown'),
            'age': pet.get('age', 'Unknown'),
            'url': pet.get('url', '#'),
            'photo': pet['photos'][0]['medium'] if pet.get('photos') else None
        }
        for pet in pets
    ]

    # Send search event to Admin Service
    event = {
        'event': 'search',
        'user_id': request.cookies.get('user_email', 'unknown'),
        'params': params,
        'results': len(processed_pets)
    }

    try:
        admin_service_url = "http://admin_service:5003/events"
        response = requests.post(admin_service_url, json=event)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send search event to Admin Service: {e}")

    return render_template("search_results.html", animals=processed_pets)

def get_petfinder_token():
    response = requests.post(
        f"{PETFINDER_API_BASE_URL}/oauth2/token",
        data={
            'grant_type': 'client_credentials',
            'client_id': PETFINDER_API_KEY,
            'client_secret': PETFINDER_API_SECRET
        }
    )
    response_data = response.json()
    if 'access_token' not in response_data:
        raise Exception("Failed to get access token")
    return response_data['access_token']

@app.route('/favorite', methods=['POST'])
def favorite_pet():
    """Send favorite pet event to Admin Service."""
    pet_id = request.form['pet_id']
    pet_name = request.form['pet_name']
    pet_breed = request.form['pet_breed']
    pet_age = request.form['pet_age']

    # Send favorite event to Admin Service
    event = {
        'event': 'favorite',
        'user_id': request.cookies.get('user_email', 'unknown'),
        'pet_id': pet_id,
        'pet_name': pet_name,
        'pet_breed': pet_breed,
        'pet_age': pet_age
    }

    try:
        admin_service_url = "http://admin_service:5003/events"
        response = requests.post(admin_service_url, json=event)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send favorite event to Admin Service: {e}")

    return redirect(request.referrer or '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
