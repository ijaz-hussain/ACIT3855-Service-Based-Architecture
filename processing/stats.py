from sqlalchemy import Column, Integer, String, DateTime
from base import Base


class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_acceleration_readings = Column(Integer, nullable=False)
    max_acceleration_speed_readings = Column(Integer, nullable=True)
    max_acceleration_watt_hours_reading = Column(Integer, nullable=True)
    num_environmental_readings = Column(Integer, nullable=False)
    max_temp_reading = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)


    def __init__(self, num_acceleration_readings, max_acceleration_speed_readings, max_acceleration_watt_hours_reading, num_environmental_readings, max_temp_reading, last_updated):
        """ Initializes a processing statistics object """
        self.num_acceleration_readings = num_acceleration_readings
        self.max_acceleration_speed_readings = max_acceleration_speed_readings
        self.max_acceleration_watt_hours_reading = max_acceleration_watt_hours_reading
        self.num_environmental_readings = num_environmental_readings
        self.max_temp_reading = max_temp_reading
        self.last_updated = last_updated


    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_acceleration_readings'] = self.num_acceleration_readings
        dict['max_acceleration_speed_reading'] = self.max_acceleration_speed_readings
        dict['max_acceleration_watt_hours_reading'] = self.max_acceleration_watt_hours_reading
        dict['num_environmental_readings'] = self.num_environmental_readings
        dict['max_temp_reading'] = self.max_temp_reading
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%SZ")

        return dict