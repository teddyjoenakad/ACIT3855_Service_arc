import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from parking_status import ParkingStatus
from payment import PaymentEvent
import datetime
import pymysql
import yaml
import logging
import logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f2:
    log_config = yaml.safe_load(f2.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
# print(DB_ENGINE)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f"connecting to DB. Hostname: {hostname}, Port: {port}")

def get_parking_status(body):
    session = DB_SESSION()
    ps = ParkingStatus(
        meter_id=body['meter_id'],
        device_id=body['device_id'],
        status=body['status'],
        spot_number=body['spot_number'],
        timestamp=body['timestamp'],
        trace_id=body['trace_id']
    )
    session.add(ps)
    session.commit()
    session.close()
    logger.debug(f'Stored parking status event for meter_id {body["meter_id"]}')
    return NoContent, 201

def get_payment_events(body):
    session = DB_SESSION()
    pe = PaymentEvent(
        meter_id=body['meter_id'],
        device_id=body['device_id'],
        amount=body['amount'],
        duration=body['duration'],
        timestamp=body['timestamp'],
        trace_id=body['trace_id']
    )
    session.add(pe)
    session.commit()
    session.close()
    logger.debug(f'Stored payment event for meter_id {body["meter_id"]}')
    return NoContent, 201

# =============== KAFKA
def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consumer on a consumer group, that only reads new messages
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False, 
                                         auto_offset_reset=OffsetType.LATEST)
    # print(consumer)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "parking_status":
            logger.info(f'Connecting to DB. Hostname: {hostname}, Port: {port}')
            session = DB_SESSION()

            ps = ParkingStatus(
                meter_id=payload['meter_id'],
                device_id=payload['device_id'],
                status=payload['status'],
                spot_number=payload['spot_number'],
                timestamp=payload['timestamp'],
                trace_id=payload['trace_id']
            )
            
            session.add(ps)
            session.commit()
            session.close()
            logger.debug(f'Stored event parking_status request with a trace id of {payload["trace_id"]}')

        elif msg["type"] == "payment":
            logger.info(f'Connecting to DB. Hostname: {hostname}, Port: {port}')
            session = DB_SESSION()

            pm = PaymentEvent(
                meter_id=payload['meter_id'],
                device_id=payload['device_id'],
                amount=payload['amount'],
                duration=payload['duration'],
                timestamp=payload['timestamp'],
                trace_id=payload['trace_id']
            )

            session.add(pm)
            session.commit()
            session.close()
            logger.debug(f'Stored event payment request with a trace id of {payload["trace_id"]}')

        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)