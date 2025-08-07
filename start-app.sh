#!/usr/bin/env bash
# start-server.sh

# python manage.py waitdb 
python manage.py migrate 
python manage.py collectstatic --no-input 
python manage.py update_ai_admins 
cd /opt/app/ 
pwd 
./start-server.sh 