import logging
import logging.handlers
import os
from kafka import KafkaAdminClient
from kafka.admin import NewTopic



cur_dir = os.path.dirname(__file__)
log_dir = os.path.join(cur_dir,"logs")
os.makedirs(log_dir,exist_ok=1)

logger = logging.getLogger("kafka_producer")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
handler = logging.FileHandler(os.path.join(log_dir,"kafka_logs.log"))
handler.setFormatter(formatter)
logger.addHandler(handler)

topic = "velib_data"
server = "kafka"

def create_kafka_topic(topic_name, num_partitions=1, replication_factor=1):
    # Initialize Kafka Admin Client
    admin_client = KafkaAdminClient(bootstrap_servers=f'{server}:9092')
    existing_topics = admin_client.list_topics()
    if topic not in existing_topics:
        new_topic = NewTopic(name=topic_name, num_partitions=num_partitions, replication_factor=replication_factor)
        try:
            admin_client.create_topics([new_topic])
            logger.debug(f"Topic '{topic_name}' created successfully.")
        except Exception as e:
            logger.error(f"Failed to create topic '{topic_name}': {e}")
    else:
        logger.error("Topic already exists!")

if __name__=="__main__":
    create_kafka_topic(topic)