# Ijaz Hussain - A00963610 4C
# ACIT 3855 - Lab 5


import connexion
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests
import datetime
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from stats import Stats
from flask_cors import CORS, cross_origin
import os
import sqlite3


if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    database = app_config["datastore"]["filename"]

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


def create_database():
    conn = sqlite3.connect(database)

    c = conn.cursor()
    c.execute(''' 
              CREATE TABLE stats 
              (id INTEGER PRIMARY KEY ASC,  
               num_acceleration_readings INTEGER NOT NULL, 
               max_acceleration_speed_readings INTEGER, 
               max_acceleration_watt_hours_reading INTEGER, 
               num_environmental_readings INTEGER NOT NULL, 
               max_temp_reading INTEGER, 
               last_updated VARCHAR(100) NOT NULL) 
              ''')

    conn.commit()
    conn.close()


if not os.path.exists(database):
    create_database()


DB_ENGINE = create_engine("sqlite:///%s" % database)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = {
            "num_acceleration_readings": 0,
            "max_acceleration_speed_reading": 0,
            "max_acceleration_watt_hours_reading": 0,
            "num_environmental_readings": 0,
            "max_temp_reading": 0,
            "last_updated": "2016-08-29T09:12:33Z"
        }
    else:
        stats = results.to_dict()

    start_timestamp = stats['last_updated']
    current_timestamp = datetime.datetime.now()
    end_timestamp = current_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")



    #get_acceleration = requests.get(app_config['eventstore1']['url'] + '?timestamp=' + previous_datetime)
    #get_environmental = requests.get(app_config['eventstore2']['url'] + '?timestamp=' + previous_datetime)
    get_acceleration = requests.get(app_config["eventstore1"]["url"] + "?start_timestamp=" + start_timestamp + "&end_timestamp=" + end_timestamp)
    get_environmental = requests.get(app_config["eventstore2"]["url"] + "?start_timestamp=" + start_timestamp + "&end_timestamp=" + end_timestamp)

    if get_acceleration.status_code != 200:
        logger.error("Received a status code of {}".format(get_acceleration.status_code))
    else:
        logger.info("Received {} events with a status code of {}".format(len(get_acceleration.json()), get_acceleration.status_code))

    if get_environmental.status_code != 200:
        logger.error("Received a status code of {}".format(get_environmental.status_code))
    else:
        logger.info("Received {} events with a status code of {}".format(len(get_environmental.json()), get_environmental.status_code))

    # Total number of acceleration readings
    stats['num_acceleration_readings'] = stats['num_acceleration_readings'] + len(get_acceleration.json())

    # Max speed reading
    max_acceleration_speed_reading = stats['max_acceleration_speed_reading']
    for event in get_acceleration.json():
        logger.debug(event)
        if event['acceleration_reading']['speed'] > max_acceleration_speed_reading:
            max_acceleration_speed_reading = event['acceleration_reading']['speed']
    stats['max_acceleration_speed_reading'] = max_acceleration_speed_reading

    # Max watt hours reading
    max_acceleration_watt_hours_reading = stats['max_acceleration_watt_hours_reading']
    for event in get_acceleration.json():
        if event['acceleration_reading']['watt_hours_per_mile'] > max_acceleration_watt_hours_reading:
            max_acceleration_watt_hours_reading = event['acceleration_reading']['watt_hours_per_mile']
    stats['max_acceleration_watt_hours_reading'] = max_acceleration_watt_hours_reading

    # Total number of environmental readings
    stats['num_environmental_readings'] = stats['num_environmental_readings'] + len(get_environmental.json())

    # Max temp reading
    max_temp_reading = stats['max_temp_reading']
    for event in get_environmental.json():
        logger.debug(event)
        if event['temperature'] > max_temp_reading:
            max_temp_reading = event['temperature']
    stats['max_temp_reading'] = max_temp_reading

    # Write updated stats to the database
    session = DB_SESSION()

    stats_new = Stats(stats["num_acceleration_readings"],
                  stats["max_acceleration_speed_reading"],
                  stats["max_acceleration_watt_hours_reading"],
                  stats["num_environmental_readings"],
                  stats["max_temp_reading"],
                  current_timestamp)

    session.add(stats_new)

    session.commit()
    session.close()

    logger.debug("Updated stats values: {}".format(stats))

    logger.info("End Periodic Processing")


def get_stats():
    """ Receives acceleration and environmental readings processed statistics """
    logger.info("Request has started")

    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc()).first()
    session.close()

    if not results:
        stats = {
            "num_acceleration_readings": 0,
            "max_acceleration_speed_reading": 0,
            "max_acceleration_watt_hours_reading": 0,
            "num_environmental_readings": 0,
            "max_temp_reading": 0,
            "last_updated": "2016-08-29T09:12:33Z"
        }
    else:
        stats = results.to_dict()

    logger.debug(stats)

    logger.info("Request has completed")

    return stats, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100, use_reloader=False)