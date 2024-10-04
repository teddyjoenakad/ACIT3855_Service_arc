import connexion
from connexion import NoContent
import json
import requests
import datetime
import yaml
import logging
import logging.config
import uuid

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f2:
    log_config = yaml.safe_load(f2.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def log_data(event, event_type):
    header = {"Content-Type": "application/json"}
    
    trace_id = str(uuid.uuid4())  # Generate a unique trace ID
    event["trace_id"] = trace_id
    body = json.dumps(event)

    # header['trace_id'] = trace_id

    logger.info(f'Received event {event_type} request with a trace id of {trace_id}')
    
    if event_type == "parking_status":
        url = app_config['eventstore1']['url']
    elif event_type == "payment":
        url = app_config['eventstore2']['url']
    else:
        logger.error(f'Unknown event type: {event_type}')
        return None, 400

    response = requests.post(url, headers=header, data=body)
    
    logger.info(f'Returned event {event_type} response (Id: {trace_id}) with status {response.status_code}')
    
    return response.text, response.status_code

def parking_status(body):
    res = log_data(body, "parking_status")
    return NoContent, res[1]

def payment(body):
    res = log_data(body, "payment")
    return NoContent, res[1]

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
