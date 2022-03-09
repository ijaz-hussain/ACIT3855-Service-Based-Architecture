# Ijaz Hussain - A00963610 4C
# ACIT 3855 - Lab 4

import connexion
import mysql.connector
import pymysql
import yaml
import logging
import datetime
import logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from acceleration_reading import AccelerationReading
from environmental_reading import EnvironmentalReading
from sqlalchemy import and_


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    user = app_config["datastore"]["user"]
    password = app_config["datastore"]["password"]
    hostname = app_config["datastore"]["hostname"]
    port = app_config["datastore"]["port"]
    db = app_config["datastore"]["db"]


with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


# Create a custom logger
logger = logging.getLogger('basicLogger')


DB_ENGINE = create_engine("mysql+pymysql://{}:{}@{}:{}/{}".format(user, password, hostname, port, db))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info("Connecting to DB. Hostname:{}, Port:{}".format(hostname, port))

def acceleration_reading(body):
    """ Receives an acceleration reading """

    session = DB_SESSION()

    ar = AccelerationReading(body['vin_id'],
                             body['acceleration_reading']['speed'],
                             body['acceleration_reading']['watt_hours_per_mile'],
                             body['estimated_range'],
                             body['timestamp'],
                             body['trace_id'])

    session.add(ar)

    session.commit()
    session.close()

    received_event = "Stored event {} request with a trace id of {}".format("acceleration reading", body['trace_id'])
    logger.debug(received_event)


def environmental_reading(body):
    """ Receives an environmental reading """

    session = DB_SESSION()

    er = EnvironmentalReading(body['vin_id'],
                              body['elevation'],
                              body['gps_location'],
                              body['grade_incline'],
                              body['temperature'],
                              body['trace_id'])

    session.add(er)

    session.commit()
    session.close()

    received_event = "Stored event {} request with a trace id of {}".format("environmental reading", body['trace_id'])
    logger.debug(received_event)


def get_acceleration_readings(start_timestamp, end_timestamp):
    """ Gets new acceleration readings after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(AccelerationReading).filter(and_(AccelerationReading.date_created >= start_timestamp_datetime, AccelerationReading.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for acceleration readings after %s returns %d results" %
                (start_timestamp, len(results_list)))

    return results_list, 200


def get_environmental_readings(start_timestamp, end_timestamp):
    """ Gets new environmental readings after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    readings = session.query(EnvironmentalReading).filter(and_(EnvironmentalReading.date_created >= start_timestamp_datetime, EnvironmentalReading.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for environmental readings after %s returns %d results" %
                (start_timestamp, len(results_list)))

    return results_list, 200


def process_messages():
    """ Process event messages """
    hostname1 = "%s:%d" % (app_config["events"]["hostname"], app_config["events"]["port"])
    client = KafkaClient(hosts=hostname1)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    # Create a consumer on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue).
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]

        if msg["type"] == "acceleration":  # Change this to your event type
        # Store the event1 (i.e., the payload) to the DB
            logger.info("Storing acceleration event")
            acceleration_reading(payload)
        elif msg["type"] == "environmental":  # Change this to your event type
        # Store the event2 (i.e., the payload) to the DB
            logger.info("Storing environmental event")
            environmental_reading(payload)

        # Commit the new message as being read
        consumer.commit_offsets()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)