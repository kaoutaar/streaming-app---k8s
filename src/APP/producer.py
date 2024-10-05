import logging
import logging.handlers
import urllib.request
import time
from kafka import KafkaProducer
from create_topic import logger




key = "c1d0cfc0377b8d04d9179d1c3f7a80e2491b30c3"
stations_url = f"https://api.jcdecaux.com/vls/v1/stations?&apiKey={key}" #all stations of all available cities
client = "JCDecaux API"
server = 'kafka'
topic = "velib_data"

logger.debug(f"Data stream from {client} to Kafka topic {topic}")


def send_api_data():
    try:
        producer = KafkaProducer(bootstrap_servers=[f'{server}:9092'], 
                                 client_id=client,
                                 acks=1)
        resp_stations = urllib.request.urlopen(stations_url)
        if resp_stations.getcode()==200:
            msg = resp_stations.read()
            producer.send(topic, msg)
            print("msg sent")
        else:
            stations_info = {"status_code":resp_stations.getcode(), 'headers':resp_stations.headers}
            logger.error(stations_info, exc_info=True)

    except Exception as e:
        logger.error(e, exc_info=True)
        producer.close()

if __name__=="__main__":
    send_api_data()

# try:
#     while True:
#         send_api_data()
#         time.sleep(20)
# except KeyboardInterrupt:
#     print("kafka terminating...")
    