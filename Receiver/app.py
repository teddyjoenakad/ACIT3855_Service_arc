import connexion
from connexion import NoContent
import json
from datetime import datetime
import os.path

MAX_EVENTS = 100
EVENT_FILE = "events.json"

def log_data(event, event_type):
    provided_timestamp = event['timestamp']
    received_timestamp = datetime.strptime(provided_timestamp, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")

    if event_type == "status":
        new_item = {
            "received_timestamp": received_timestamp,
            "msg_data": f"Meter ID {event['meter_id']} status is {'free' if event['status'] else 'occupied'}."
        }
    elif event_type == "payment":
        new_item = {
            "received_timestamp": received_timestamp,
            "msg_data": f"Meter ID {event['meter_id']} received payment of ${event['amount']}."
        }
    
    if os.path.isfile(EVENT_FILE) and os.path.getsize(EVENT_FILE) > 0:
        with open(EVENT_FILE, 'r') as file_read:
                old_data = json.load(file_read)
        if event_type == "status":
            old_data["num_status"] += 1
            old_data["recent_status"].insert(0, new_item)
            if len(old_data["recent_status"]) >= MAX_EVENTS:
                old_data["recent_status"].pop()  # Remove the oldest event if more than MAX_EVENTS

        elif event_type == "payment":
            old_data["num_payment"] += 1
            old_data["recent_payment"].insert(0, new_item)
            if len(old_data["recent_payment"]) >= MAX_EVENTS:
                old_data["recent_payment"].pop()

    else:
        old_data = {"num_status": 0, "recent_status": [], "num_payment": 0, "recent_payment": []}
    
    with open(EVENT_FILE, 'w') as file_write:
        json.dump(old_data, file_write, indent=2)

def report_parking_status(body):
    log_data(body, "status")
    return NoContent, 201  

def report_payment_event(body):
    log_data(body, "payment")
    return NoContent, 201  

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
