from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required

app = Flask(__name__)
app.secret_key = '1'  # Set a secure secret key for session handling

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Dummy user store
users = {
    'user1@example.com': {'password': 'password123', 'events': []},
    'user2@example.com': {'password': 'mypassword', 'events': []}
}

class User(UserMixin):
    """User class for Flask-Login."""
    def __init__(self, email):
        self.id = email
        self.events = []  # Add the events attribute to track user-specific events


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id in users:
        user = User(user_id)
        user.events = users[user_id].get('events', [])  # Load events for the user
        return user
    return None


# Routes

from flask import make_response

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            login_user(User(email))
            flash('Login successful!', 'success')

            # Set a cookie with the user's email for the pet search service
            response = make_response(redirect('http://localhost:5002/'))
            response.set_cookie('user_email', email)
            return response
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout and redirect to login."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/search_menu', methods=['GET', 'POST'])
@login_required
def search_menu():
    """Search menu form."""
    if request.method == 'POST':
        params = {key: value for key, value in request.form.items() if value}
        current_user.events.append({'event': 'search', 'params': params})
        users[current_user.id]['events'] = current_user.events  # Save back to the user store
        return redirect(url_for('search_results', **params))
    return render_template('search_menu.html')


@app.route('/search')
@login_required
def search_results():
    """Display search results."""
    # Dummy results for demonstration
    results = [
        {'id': '1', 'name': 'Fluffy', 'breed': 'Chihuahua', 'age': '2 years'},
        {'id': '2', 'name': 'Buddy', 'breed': 'Labrador', 'age': '3 years'}
    ]
    return render_template('search_results.html', results=results)

@app.route('/favorite', methods=['POST'])
@login_required
def favorite_pet():
    """Favorite a pet."""
    pet_id = request.form['pet_id']
    pet_name = request.form['pet_name']
    current_user.events.append({'event': 'favorite', 'pet_id': pet_id, 'pet_name': pet_name})
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard showing user activity."""
    user_events = users[current_user.id]['events']
    searches = [e for e in user_events if e['event'] == 'search']
    favorites = [e for e in user_events if e['event'] == 'favorite']
    return render_template('dashboard.html', searches=searches, favorites=favorites)

@app.route('/events', methods=['POST'])
def receive_event():
    """Receive and log events from other services."""
    event = request.json
    print(f"Received event: {event}")  # Add this line for debugging
    if not event or 'user_id' not in event:
        return jsonify({'message': 'Invalid event data'}), 400
    user_id = event['user_id']
    if user_id in users:
        users[user_id]['events'].append(event)
        print(f"Updated events for user {user_id}: {users[user_id]['events']}")  # Debug logs
    else:
        print(f"Unknown user: {user_id}")
    return jsonify({'message': 'Event received'}), 201




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
