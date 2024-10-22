#!/usr/bin/env bash
# start-server.sh

# python manage.py waitdb 
python manage.py migrate 
python manage.py collectstatic --no-input
cd /opt/app/ 
pwd 
./start-server.sh 