import connexion
from connexion import NoContent
import json
from datetime import datetime
import os.path
import requests
import yaml
import logging.config 
import logging
import uuid

MAX_EVENTS = 5
EVENT_FILE = "events.json"
STORAGE_SERVICE_URL = "http://localhost:8090"

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

#print(app_config['eventstore1']['url'])

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
    trace_id = str(uuid.uuid4())  # Generate unique trace ID
    logger.info(f"Received event parking_status request with a trace id of {trace_id}")
    
    # Use the URL from the configuration file
    response = requests.post(app_config['eventstore1']['url'], json=body, headers={"trace_id": trace_id})
    
    if response.status_code == 201:
        logger.info(f"Returned event parking_status response (Id: {trace_id}) with status {response.status_code}")
        return NoContent, 201
    else:
        logger.error(f"Error in parking_status: {response.text}")
        return NoContent, response.status_code


def payment(body):
    trace_id = str(uuid.uuid4())  # Generate unique trace ID
    logger.info(f"Received event payment request with a trace id of {trace_id}")
    
    # Use the URL from the configuration file
    response = requests.post(app_config['eventstore2']['url'], json=body, headers={"trace_id": trace_id})
    
    if response.status_code == 201:
        logger.info(f"Returned event payment response (Id: {trace_id}) with status {response.status_code}")
        return NoContent, 201
    else:
        logger.error(f"Error in payment: {response.text}")
        return NoContent, response.status_code


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)