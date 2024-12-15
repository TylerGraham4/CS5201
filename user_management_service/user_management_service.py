from flask import Flask, request, jsonify, render_template, redirect, url_for
import requests

app = Flask(__name__)

# In-memory database for simplicity
users = {}  # This will dynamically store user data (email, password, events)
ADMIN_SERVICE_URL = "http://admin_service:5003/"  # URL to send events

@app.route('/register_page', methods=['GET'])
def register_page():
    """Serve the user registration form."""
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user."""
    # Handle API and form submissions
    if request.content_type == 'application/json':
        data = request.json
    else:
        data = {'email': request.form.get('email'), 'password': request.form.get('password')}

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'Email and password are required'}), 400
    if data['email'] in users:
        return jsonify({'message': 'User already exists'}), 400

    # Add the user to the in-memory database
    users[data['email']] = {'password': data['password'], 'events': []}

    # Notify the Admin Service to update its user store
    admin_service_user_data = {
        'email': data['email'],
        'password': data['password']  # Optional: Avoid sending plain text passwords if possible
    }
    try:
        requests.post(f"{ADMIN_SERVICE_URL}/add_user", json=admin_service_user_data)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send user data to Admin Service: {e}")

    # Notify the Admin Service of the registration event
    event = {
        'event': 'user_registered',
        'user_id': data['email'],
        'details': {'favorites': []}
    }
    try:
        requests.post(ADMIN_SERVICE_URL, json=event)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send registration event to Admin Service: {e}")

    # Redirect to success page or return a JSON response
    if request.content_type != 'application/json':
        return redirect(url_for('register_success'))
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/register_success', methods=['GET'])
def register_success():
    """Display a success message after registration."""
    return render_template("register_success.html")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
