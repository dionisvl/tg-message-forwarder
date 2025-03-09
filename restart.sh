#!/bin/bash
# Path to log file
LOG_FILE="logs/restart.log"

# Log restart time
echo "Restarting containers at $(date)" >> $LOG_FILE

# Perform restart
cd /home/tgbot/tg-message-forwarder
make down >> $LOG_FILE 2>&1
sleep 10
make up >> $LOG_FILE 2>&1

echo "Restart completed at $(date)" >> $LOG_FILE
echo "---------------------------------" >> $LOG_FILE
