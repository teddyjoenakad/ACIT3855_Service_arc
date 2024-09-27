import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from parking_status import ParkingStatus
from payment import PaymentEvent
from datetime import datetime

DB_ENGINE = create_engine("sqlite:///parking_events.sqlite")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

def parking_status(body):
    """ Receives a parking status update """
    session = DB_SESSION()

    parking_status = ParkingStatus(
        meter_id=body['meter_id'],
        device_id=body['device_id'],
        status=body['status'],
        spot_number=body['spot_number'],
        timestamp=body['timestamp']
    )

    session.add(parking_status)
    session.commit()
    session.close()

    return NoContent, 201

def payment(body):
    """ Receives a payment event """
    session = DB_SESSION()

    payment_event = PaymentEvent(
        meter_id=body['meter_id'],
        device_id=body['device_id'],
        amount=body['amount'],
        duration=body['duration'],
        timestamp=body['timestamp']
    )

    session.add(payment_event)
    session.commit()
    session.close()

    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8090)
