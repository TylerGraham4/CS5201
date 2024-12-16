# README for Pet Search Application

## Application Overview

The Pet Search Application is a multi-service system designed to enable users to search for adoptable pets, favorite pets, and manage user activity and events. The application integrates with the Petfinder API to fetch pet data and features three primary services:

1. **Admin Service**: Manages user authentication, handles events, and tracks user activity.
2. **Pet Search Service**: Interfaces with the Petfinder API to provide pet search capabilities.
3. **User Management Service**: Manages user-related data and provides endpoints for user actions.

---



## Installation Instructions

### Prerequisites

- Python 3.11+
- Docker and Docker Composed Installed

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   ```

2. **Build and start the services using Docker Compose:**:
   ```bash
    docker-compose up --build -d
   ```

3. **Access the following**:

- Pet Search Service: http://localhost:5002/
- User Management Service: http://localhost:5001
- Admin Service: http://localhost:5003/login


---

## API Documentation

### Admin Service Endpoints

#### **`POST /add_user`**
- **Description**: Adds a new user to the system.
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User added successfully"
  }
  ```

#### **`POST /events`**
- **Description**: Logs an event for a user.
- **Request Body**:
  ```json
  {
    "user_id": "user@example.com",
    "event": "search",
    "params": {"breed": "Labrador"},
    "results": 5
  }
  ```
- **Response**:
  ```json
  {
    "message": "Event received"
  }
  ```

#### **`GET /dashboard`**
- **Description**: Displays the user's activity dashboard.

---

### Pet Search Service Endpoints

#### **`GET /search`**
- **Description**: Searches for pets based on user-provided criteria.
- **Query Parameters**:
  - `breed`: Breed of the pet.
  - `age`: Age range of the pet.
  - `location`: Location to search for pets.
- **Response**:
  ```json
  [
    {
      "id": "1",
      "name": "Fluffy",
      "breed": "Chihuahua",
      "age": "2 years",
      "url": "https://www.petfinder.com/..."
    }
  ]
  ```

#### **`POST /favorite`**
- **Description**: Marks a pet as a favorite for the current user.
- **Request Body**:
  ```json
  {
    "pet_id": "1",
    "pet_name": "Fluffy"
  }
  ```
- **Response**:
  ```json
  {
    "message": "Pet favorited"
  }
  ```

---

### Use Cases

1. **Search for Pets**:
   - Navigate to the Pet Search Service at `http://localhost:5002`.
   - Use the search form to specify criteria such as breed, age, or location.
   - View search results.

2. **Favorite a Pet**:
   - After searching for pets, click the "Favorite" button on a pet.
   - The pet is added to your favorites and tracked in the Admin Service.

3. **View Dashboard**:
   - Log in to the Admin Service at `http://localhost:5003/login`.
   - Access the dashboard to view your search history and favorited pets.

---

## Notes

- The application uses Flask for the backend and integrates with the Petfinder API for pet data.
- Ensure all services are running simultaneously to use the application seamlessly.
- For production deployment, use tools like Docker, Gunicorn, and Nginx to enhance scalability and performance.

