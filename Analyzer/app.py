import connexion
from connexion import NoContent
import json
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType

# Load configuration files
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f2:
    log_config = yaml.safe_load(f2.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def get_parking_status_event(index):
    """Get Parking Status Event in History"""
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["parking_topic"])]

    # Here we reset the offset on start to retrieve messages from the beginning
    # Timeout set to prevent blocking the loop if messages are continuously received
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving parking status event at index %d" % index)
    
    list_of_events = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            # Only keep messages of type 'parking_status'
            if msg['type'] == 'parking_status':
                list_of_events.append(msg)
            
            # Check if we've reached the requested index
            if len(list_of_events) > index:
                payload = list_of_events[index]
                response = {
                    "type": payload["type"],
                    "datetime": payload["datetime"],
                    "payload": payload["payload"]
                }
                return response, 200
    except IndexError:
        logger.error("No more messages found")
        logger.error("Could not find parking status event at index %d" % index)
        return {"message": "Not Found"}, 404
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"message": "Internal Server Error"}, 500


def get_payment_event(index):
    """Get Payment Event in History"""
    hostname = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["payment_topic"])]

    # Here we reset the offset on start to retrieve messages from the beginning
    # Timeout set to prevent blocking the loop if messages are continuously received
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving payment event at index %d" % index)
    
    list_of_events = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            
            # Only keep messages of type 'payment'
            if msg['type'] == 'payment':
                list_of_events.append(msg)
            
            # Check if we've reached the requested index
            if len(list_of_events) > index:
                payload = list_of_events[index]
                response = {
                    "type": payload["type"],
                    "datetime": payload["datetime"],
                    "payload": payload["payload"]
                }
                return response, 200
    except IndexError:
        logger.error("No more messages found")
        logger.error("Could not find payment event at index %d" % index)
        return {"message": "Not Found"}, 404
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"message": "Internal Server Error"}, 500


# Initialize and run the Flask app
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)