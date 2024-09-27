import connexion
from connexion import NoContent
import json
from datetime import datetime
import os.path
import requests  # Import requests to send HTTP requests

MAX_EVENTS = 5
EVENT_FILE = "events.json"
STORAGE_SERVICE_URL = "http://localhost:8090"  # URL for the Storage Service

def log_data(event, event_type):
    provided_timestamp = event['timestamp']
    received_timestamp = datetime.strptime(provided_timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
    
    if event_type == "parking_status":
        new_item = {
            "received_timestamp": received_timestamp,
            "msg_data": f"Meter ID {event['meter_id']} status is {'free' if event['status'] else 'occupied'}."
        }
    elif event_type == "payment":
        new_item = {
            "received_timestamp": received_timestamp,
            "msg_data": f"Meter ID {event['meter_id']} received payment of ${event['amount']}."
        }

    # Log data to local JSON file
    if os.path.isfile(EVENT_FILE):
        with open(EVENT_FILE, 'r') as file_read:
            try:
                old_data = json.load(file_read)
            except json.JSONDecodeError:
                old_data = {"num_status": 0, "recent_status": [], "num_payment": 0, "recent_payment": []}
    else:
        old_data = {"num_status": 0, "recent_status": [], "num_payment": 0, "recent_payment": []}
    
    if event_type == "parking_status":
        old_data["num_status"] += 1
        old_data["recent_status"].insert(0, new_item)
        if len(old_data["recent_status"]) > MAX_EVENTS:
            old_data["recent_status"].pop()  # Remove the oldest event if more than MAX_EVENTS

    elif event_type == "payment":
        old_data["num_payment"] += 1
        old_data["recent_payment"].insert(0, new_item)
        if len(old_data["recent_payment"]) > MAX_EVENTS:
            old_data["recent_payment"].pop()

    with open(EVENT_FILE, 'w') as file_write:
        json.dump(old_data, file_write, indent=4)

def parking_status(body):
    #log_data(body, "status")
    response = requests.post(f"{STORAGE_SERVICE_URL}/parking", json=body)
    
    if response.status_code == 201:
        return NoContent, 201
    else:
        print(f"Error in parking_status: {response.text}")  # Print error message
        return NoContent, response.status_code  # Return the error status code if the call fails


def payment(body):
    #log_data(body, "payment")
    response = requests.post(f"{STORAGE_SERVICE_URL}/payment", json=body)
    
    if response.status_code == 201:
        return NoContent, 201
    else:
        print(f"Error in payment: {response.text}")
        return NoContent, response.status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
