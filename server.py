import os
import re
import pytz
import json
import logging
import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
from datetime import datetime

# Create an InfluxDB client
influxdb_client = InfluxDBClient(os.environ.get("INFLUXDB_HOST", "influxdb"))
influxdb_client.switch_database(os.environ.get("INFLUXDB_DB", "influxdb_data_db"))
# query = 'DROP SERIES FROM /.*/'
# influxdb_client.query(query)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # client.subscribe("UPB/#")
    # client.subscribe("Dorinel/#")
    client.subscribe("#")
    

# Define the callback function for the MQTT client
def on_message(client, userdata, message):
    # Extract the topic from the message
    topic = message.topic
    topic_matches = re.match(r"(?P<location>[^/]*?)/(?P<station>.*)", topic)

    # If the topic is not in the correct format, log the error and return
    if not topic_matches:
        logging.info("Wrong format {topic}".format(topic=topic))
        return

    location = topic_matches['location']
    station = topic_matches['station']

    # Log the message if DEBUG_DATA_FLOW is 'true'
    if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
        log_message = f"Received a message by topic {location}/{station}"
        logging.info(log_message)

    payload = json.loads(message.payload)

    # Extract the timestamp from the payload if it doesn't exist, use the current time
    timestamp = payload.get('timestamp', datetime.now(pytz.timezone("Europe/Bucharest")).strftime("%Y-%m-%dT%H:%M:%S%z"))

    # Log the timestamp if DEBUG_DATA_FLOW is 'true'
    if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
        timestamp_log_message = f"Data timestamp is {timestamp}" if 'timestamp' in payload else "Data timestamp is NOW"
        logging.info(timestamp_log_message)

    # Create a list of 'to-add' data
    db_data = []


    for key, value in payload.items():
        if isinstance(value, str):
            continue

        # Log the field if DEBUG_DATA_FLOW is 'true'
        if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
            log_message = f"{location}.{station}.{key} {value}"
            logging.info(log_message)

        # Build the measurement as <station>.<key>
        measurement = f"{station}.{key}"

        # Build the entry object
        entry = {
            'measurement': measurement,
            'tags': {
                'location': location,
                'station': station,
            },
            'fields': {
                'value': value
            },
            'time': timestamp
        }

        db_data.append(entry)

    if db_data:
        if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
            logging.info(f"Adding data to the database: {db_data}")

        try:
            influxdb_client.write_points(db_data)
        except Exception as e:
            logging.error("Failed to write data to InfluxDB: " + str(e))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
# Configure the logging module
logging.basicConfig(filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

# client.connect("broker.hivemq.com", 1883, 60)
client.connect(os.environ.get("MQTTBROKER_HOST", "mqtt_broker"))

client.loop_forever()
