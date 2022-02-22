# Ijaz Hussain - A00963610 4C
# ACIT 3855 - Lab 4


import requests
import connexion
import yaml
import logging
import random
import logging.config
import datetime
import json
from pykafka import KafkaClient
from connexion import NoContent


with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    acceleration_url = app_config["eventstore1"]["url"]
    environmental_url = app_config["eventstore2"]["url"]
    kafka_server = app_config["events"]["hostname"]
    kafka_port = app_config["events"]["port"]
    tp = app_config["events"]["topic"]



with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)


# Create a custom logger
logger = logging.getLogger('basicLogger')


# Your functions here
def acceleration_reading(body):
    # POST request
    headers = {"content-type": "application/json"}
    trace_id = str(random.randint(0, 9999999999))
    event_name = acceleration_url.split("/")[-1]
    event_request = "Received event {} reading with a trace id of {}".format(event_name, trace_id)
    logger.info(event_request)
    body['trace_id'] = trace_id
    #response = requests.post(acceleration_url, json=body, headers=headers)
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[str.encode(tp)]
    producer = topic.get_sync_producer()
    msg = {"type": "acceleration",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    returned_event = "Returned event {} reading response id:{} reading with status {}".format(event_name, trace_id, 201)
    logger.info(returned_event)

    return NoContent, 201


def environmental_reading(body):
    # POST request
    headers = {"content-type": "application/json"}
    trace_id = str(random.randint(0, 9999999999))
    event_name = environmental_url.split("/")[-1]
    event_request = "Received event {} reading with a trace id of {}".format(event_name, trace_id)
    logger.info(event_request)
    body['trace_id'] = trace_id
    #response = requests.post(environmental_url, json=body, headers=headers)
    client = KafkaClient(hosts='{}:{}'.format(kafka_server, kafka_port))
    topic = client.topics[str.encode(tp)]
    producer = topic.get_sync_producer()
    msg = {"type": "environmental",
           "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
           "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    returned_event = "Returned event {} reading response id:{} reading with status {}".format(event_name, trace_id, 201)
    logger.info(returned_event)

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)


if __name__ == "__main__":
    app.run(port=8080)