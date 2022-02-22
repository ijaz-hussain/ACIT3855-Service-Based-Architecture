from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class AccelerationReading(Base):
    """ Acceleration Reading """

    __tablename__ = "acceleration_reading"

    id = Column(Integer, primary_key=True)
    vin_id = Column(String(17), nullable=False)
    speed = Column(Integer, nullable=False)
    watt_hours_per_mile = Column(Integer, nullable=False)
    estimated_range = Column(Integer, nullable=False)
    timestamp = Column(String(100), nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, vin_id, speed, watt_hours_per_mile, estimated_range, timestamp, trace_id):
        """ Initializes an acceleration reading """
        self.vin_id = vin_id
        self.speed = speed
        self.watt_hours_per_mile = watt_hours_per_mile
        self.estimated_range = estimated_range
        self.timestamp = timestamp
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary representation of an acceleration reading """
        dict = {}
        dict['id'] = self.id
        dict['vin_id'] = self.vin_id
        dict['acceleration_reading'] = {}
        dict['acceleration_reading']['speed'] = self.speed
        dict['acceleration_reading']['watt_hours_per_mile'] = self.watt_hours_per_mile
        dict['estimated_range'] = self.estimated_range
        dict['timestamp'] = self.timestamp
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict