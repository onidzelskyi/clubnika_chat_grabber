#!/bin/sh

# Add next line to crontab e.g. crontab -e
# 0 2 * * * /home/ubuntu/clubnika_chat_grabber/scheduler.py

EMAIL='alexey.education@gmail.com'
WORK_DIR='/home/ubuntu/clubnika_chat_grabber'
BRANCH='development'
REPORT_FILE='report.txt'
CLASSIFY_CMD='classifier.py'
GRAB_CMD='grab_chat.py -u'

# Change working directory to repo dir
cd $WORK_DIR

# Update repo
git checkout $BRANCH
git pull origin $BRANCH

# Install dependencies
#sudo pip install -r requirements.txt

# Export chromedriver PATH
export PATH=$(pwd):$PATH
echo $PATH

# Grab unfetched data
$(pwd)/$GRAB_CMD

# Process data
$(pwd)/$CLASSIFY_CMD

# Send results by mail
cat $REPORT_FILE | mail -s "Chat report" -A $REPORT_FILE $EMAIL
