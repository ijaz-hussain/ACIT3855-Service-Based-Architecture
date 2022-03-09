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


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create a basic logger
logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"])
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

    previous_datetime = stats['last_updated']
    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    #get_acceleration = requests.get(app_config['eventstore1']['url'] + '?timestamp=' + previous_datetime)
    #get_environmental = requests.get(app_config['eventstore2']['url'] + '?timestamp=' + previous_datetime)
    get_acceleration = requests.get(app_config["eventstore1"]["url"] + "/acceleration?start_timestamp=" + previous_datetime + "&end_timestamp=" + current_timestamp)
    get_environmental = requests.get(app_config["eventstore2"]["url"] + "/environmental?start_timestamp=" + previous_datetime + "&end_timestamp=" + current_timestamp)

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

