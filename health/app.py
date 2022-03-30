# Ijaz Hussain - A00963610 4C
# ACIT 3855 - Assignment 3

import requests
import connexion
import yaml
import logging
import logging.config
import datetime
import json
import time
from pykafka import KafkaClient
from connexion import NoContent
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from health import Health
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


# Your functions here
def create_database():
    conn = sqlite3.connect(database)

    c = conn.cursor()
    c.execute(''' 
                  CREATE TABLE health 
                  (id INTEGER PRIMARY KEY ASC,  
                   receiver VARCHAR NOT NULL, 
                   storage VARCHAR NOT NULL, 
                   processing VARCHAR NOT NULL,
                   audit VARCHAR NOT NULL,
                   last_update VARCHAR(100) NOT NULL) 
                  ''')

    conn.commit()
    conn.close()

if not os.path.exists(database):
    create_database()

DB_ENGINE = create_engine("sqlite:///%s" % database)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def populate_health():
    logger.info("Start Periodic Health Check")

    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_update.desc()).first()
    session.close()

    if not results:
        health = {
            "receiver": "Running",
            "storage": "Down",
            "processing": "Running",
            "audit": "Running",
            "last_update": "2016-08-29T09:12:33Z"
        }
    else:
        health = results.to_dict()

    get_receiver_health = requests.get(app_config["receiver"]["url"], timeout=5)
    get_storage_health = requests.get(app_config["storage"]["url"], timeout=5)
    get_processing_health = requests.get(app_config["processing"]["url"], timeout=5)
    get_audit_health = requests.get(app_config["audit_log"]["url"], timeout=5)

    if get_receiver_health.status_code == 200:
        logger.info("Receiver is running with a status code of {}".format(get_receiver_health.status_code))
        receiver_status = "Running"
        health['receiver_status'] = receiver_status
    else:
        logger.error("Receiver is not running.")
        receiver_status = "Down"
        health['receiver_status'] = receiver_status

    if get_storage_health.status_code == 200:
        logger.info("Storage is running with a status code of {}".format(get_storage_health.status_code))
        storage_status = "Running"
        health['storage_status'] = storage_status
    else:
        logger.error("Storage is not running.")
        storage_status = "Down"
        health['storage_status'] = storage_status

    if get_processing_health.status_code == 200:
        logger.info("Processing is running with a status code of {}".format(get_processing_health.status_code))
        processing_status = "Running"
        health['processing_status'] = processing_status
    else:
        logger.error("Processing is not running.")
        processing_status = "Down"
        health['processing_status'] = processing_status

    if get_audit_health.status_code == 200:
        logger.info("Audit is running with a status code of {}".format(get_audit_health.status_code))
        audit_status = "Running"
        health['audit_status'] = audit_status
    else:
        logger.error("Audit is not running.")
        audit_status = "Down"
        health['audit_status'] = audit_status

    timestamp = datetime.datetime.now()
    current_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

    session = DB_SESSION()

    health_new = Health(health["receiver_status"],
                      health["storage_status"],
                      health["processing_status"],
                      health["audit_status"],
                      timestamp)

    session.add(health_new)

    session.commit()
    session.close()


def get_health():
    logger.info("Request has started")

    session = DB_SESSION()
    results = session.query(Health).order_by(Health.last_update.desc()).first()
    session.close()

    if not results:
        health = {
            "receiver": "Running",
            "storage": "Down",
            "processing": "Running",
            "audit": "Running",
            "last_update": "2016-08-29T09:12:33Z"
        }
    else:
        health = results.to_dict()

    logger.debug(health)

    logger.info("Request has completed")

    return health, 200


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_health, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path="/health", strict_validation=True, validate_responses=True)
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'


if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'


if __name__ == "__main__":
    init_scheduler()
    app.run(port=8120, use_reloader=False)