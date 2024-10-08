#!/bin/sh

/opt/bitnami/spark/sbin/start-connect-server.sh --packages org.apache.spark:spark-connect_2.12:3.5.2 &
sleep 120
python /opt/bitnami/spark/src/stream_consumer.py


