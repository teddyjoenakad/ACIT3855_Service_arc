from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql.functions import now
from base import Base

class PaymentEvent(Base):
    """ Payment Event """

    __tablename__ = "payment_event"

    id = Column(Integer, primary_key=True)
    meter_id = Column(String(250), nullable=False)
    device_id = Column(String(250), nullable=False)
    amount = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, meter_id, device_id, amount, duration, timestamp):
        """ Initializes a payment event """
        self.meter_id = meter_id
        self.device_id = device_id
        self.amount = amount
        self.duration = duration
        self.timestamp = timestamp
        self.date_created = now()  # Sets the date/time record is created

    def to_dict(self):
        """ Dictionary Representation of a payment event """
        return {
            'id': self.id,
            'meter_id': self.meter_id,
            'device_id': self.device_id,
            'amount': self.amount,
            'duration': self.duration,
            'timestamp': self.timestamp,
            'date_created': self.date_created
        }
