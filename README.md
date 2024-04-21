Steps to run:

1. docker swarm init --advertise-addr 127.0.0.1
2. ./run.sh
3. python3 server.py
4. python3 test.py
5. populate the grafana by hand


The server.py script appears to be an MQTT message handler that receives messages, 
extracts information from the message, logs relevant details based on environmental 
settings, and stores valid data in an InfluxDB database. Here are explanations for 
some of the implementation decisions:

Regular Expression for Topic Parsing:
topic_matches = re.match(r"(?P<location>[^/]*?)/(?P<station>.*)", topic)
This regular expression is used to extract location and station from the MQTT topic. 
It uses named capturing groups to make it more readable and to facilitate accessing 
the matched values later.

Timestamp Handling:
timestamp = payload.get('timestamp', datetime.now(pytz.timezone("Europe/Bucharest")).
strftime("%Y-%m-%dT%H:%M:%S%z"))
If the payload contains a 'timestamp' key, it is extracted. If not, the current time 
in the "Europe/Bucharest" timezone is used. The timestamp is formatted in a way compatible 
with InfluxDB.

Logging for Debugging:
if os.environ.get("DEBUG_DATA_FLOW", False) == 'true':
    logging.info(f"Received a message by topic {location}/{station}")
    logging.info(f"Data timestamp is {timestamp}" if 'timestamp' in payload else "Data
    timestamp is NOW")
    logging.info(f"{location}.{station}.{key} {value}")
    logging.info(f"Adding data to the database: {db_data}")
Log messages are conditionally generated based on the DEBUG_DATA_FLOW environment variable.
This allows debugging information to be printed only when debugging is enabled.

InfluxDB Data Structure:
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
The data structure for each entry is organized to match the InfluxDB data model. Each entry
has a measurement, tags, fields, and a timestamp.

Checking Numeric Values:
if not (isinstance(value, (int, float)) or key == "timestamp"):
    continue
This condition ensures that only numeric values (integers or floats) or the 'timestamp' key
are processed. Other non-numeric values are skipped.

Health Checks for MQTT and InfluxDB:
influxdb_client = InfluxDBClient(os.environ.get("INFLUXDB_HOST", "influxdb"))
client.connect(os.environ.get("MQTTBROKER_HOST", "mqtt_broker"))
The InfluxDB and MQTT broker hosts are retrieved from environment variables, allowing
flexibility. These checks ensure that the script only starts when these services are available.

Configuring Logging:
logging.basicConfig(filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)
The logging module is configured to write log messages to the console with a timestamp.

Environmental Configuration:
influxdb_client = InfluxDBClient(os.environ.get("INFLUXDB_HOST", "influxdb"))
client.connect(os.environ.get("MQTTBROKER_HOST", "mqtt_broker"))
The use of os.environ.get allows default values to be provided if the corresponding
environment variables are not set. This adds flexibility for different deployment scenarios.

Looping MQTT Client:
client.loop_forever()
The script enters a loop to listen for MQTT messages indefinitely. This is typical for
MQTT clients, as they continuously wait for incoming messages.
