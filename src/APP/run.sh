#!/bin/sh
python /app/create_topic.py
# Start cron service
cron
# Add the producer script to cron (running every minute) and redirect stdout and stderr to log file
echo "* * * * * /usr/local/bin/python /app/producer.py >> /app/logs/cronlogs.log 2>&1" | crontab -
#launch consumer script
python /app/stream_consumer.py &
#in another shell wait 80 sec and launch the streamlit app, enough time to let the other services launch correctly
sleep 80 
#launch the webapp and redirect stderr to log file
streamlit run /app/velib_app.py 2>> /app/logs/applogs.log

