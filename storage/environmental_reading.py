from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class EnvironmentalReading(Base):
    """ Environmental Reading """

    __tablename__ = "environmental_reading"

    id = Column(Integer, primary_key=True)
    vin_id = Column(String(17), nullable=False)
    elevation = Column(Integer, nullable=False)
    gps_location = Column(String(100), nullable=False)
    grade_incline = Column(Integer, nullable=False)
    temperature = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, vin_id, elevation, gps_location, grade_incline, temperature, trace_id):
        """ Initializes an environmental reading """
        self.vin_id = vin_id
        self.elevation = elevation
        self.gps_location = gps_location
        self.grade_incline = grade_incline
        self.temperature = temperature
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary representation of an environmental reading """
        dict = {}
        dict['id'] = self.id
        dict['vin_id'] = self.vin_id
        dict['elevation'] = self.elevation
        dict['gps_location'] = self.gps_location
        dict['grade_incline'] = self.grade_incline
        dict['temperature'] = self.temperature
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict