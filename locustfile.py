from locust import HttpUser, TaskSet, task, between, events
import statistics

# Metrics storage
metrics = {
    "requests": {},
    "failures": 0,
    "total_requests": 0,
    "latencies": [],
    "response_sizes": [],
}

# Task for Admin Service
class AdminServiceBehavior(TaskSet):
    @task
    def login(self):
        """Simulate user login."""
        self.client.post("/login", data={"email": "user1@example.com", "password": "password123"})

    @task
    def dashboard(self):
        """Access user dashboard."""
        self.client.get("/dashboard")

    @task
    def add_user(self):
        """Simulate adding a new user."""
        with self.client.post("/add_user", json={"email": "newuser@example.com", "password": "securepassword"}, catch_response=True) as response:
            self._record_metrics(response, "/add_user")

# Task for Pet Search Service
class PetSearchServiceBehavior(TaskSet):
    @task
    def search_menu(self):
        """Access the search menu."""
        self.client.get("/")

    @task
    def search_pets(self):
        """Search for pets."""
        with self.client.get("/search", params={"breed": "Chihuahua", "age": "young"}, catch_response=True) as response:
            self._record_metrics(response, "/search")

    @task
    def favorite_pet(self):
        """Favorite a pet."""
        self.client.post("/favorite", data={"pet_id": "1", "pet_name": "Fluffy", "pet_breed": "Labrador", "pet_age": "2 years"})

# Task for User Management Service
class UserManagementServiceBehavior(TaskSet):
    @task
    def register_page(self):
        """Access the user registration page."""
        self.client.get("/register_page")

    @task
    def register_user(self):
        """Register a new user."""
        with self.client.post("/register", json={"email": "testuser@example.com", "password": "testpassword"}, catch_response=True) as response:
            self._record_metrics(response, "/register")

# Utility to record metrics
def record_metrics(response, endpoint):
    metrics["total_requests"] += 1
    if endpoint not in metrics["requests"]:
        metrics["requests"][endpoint] = {"count": 0, "latencies": [], "failures": 0}
    
    metrics["requests"][endpoint]["count"] += 1

    if response.status_code == 200:
        latency = response.elapsed.total_seconds() * 1000  # Convert to ms
        metrics["latencies"].append(latency)
        metrics["requests"][endpoint]["latencies"].append(latency)
        metrics["response_sizes"].append(len(response.content))
    else:
        metrics["failures"] += 1
        metrics["requests"][endpoint]["failures"] += 1

# Define Users for the Application
class AdminServiceUser(HttpUser):
    tasks = [AdminServiceBehavior]
    wait_time = between(1, 3)
    host = "http://localhost:5003"

class PetSearchServiceUser(HttpUser):
    tasks = [PetSearchServiceBehavior]
    wait_time = between(1, 3)
    host = "http://localhost:5002"

class UserManagementServiceUser(HttpUser):
    tasks = [UserManagementServiceBehavior]
    wait_time = between(1, 3)
    host = "http://localhost:5001"

# Event hook to generate a report at the end of the test
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    print("\n=== Performance Report ===")
    total_requests = metrics["total_requests"]
    failures = metrics["failures"]
    median_latency = statistics.median(metrics["latencies"]) if metrics["latencies"] else 0
    average_latency = statistics.mean(metrics["latencies"]) if metrics["latencies"] else 0
    average_response_size = statistics.mean(metrics["response_sizes"]) if metrics["response_sizes"] else 0

    print(f"Total Requests: {total_requests}")
    print(f"Total Failures: {failures}")
    print(f"Median Latency: {median_latency:.2f} ms")
    print(f"Average Latency: {average_latency:.2f} ms")
    print(f"Average Response Size: {average_response_size:.2f} bytes")

    for endpoint, data in metrics["requests"].items():
        median_endpoint_latency = statistics.median(data["latencies"]) if data["latencies"] else 0
        print(f"\nEndpoint: {endpoint}")
        print(f"  Requests: {data['count']}")
        print(f"  Failures: {data['failures']}")
        print(f"  Median Latency: {median_endpoint_latency:.2f} ms")
