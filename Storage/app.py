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

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f2:
    log_config = yaml.safe_load(f2.read())
    logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

print('here')

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']

print(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def parking_status(body):
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

def payment(body):
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
    logger.debug(f'Stored payment event for trace_id {body["trace_id"]}')
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)