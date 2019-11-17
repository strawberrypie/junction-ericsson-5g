#!/bin/bash
while ! nc -z localhost 8080; do sleep 1; done
TOKEN=$(python3 /root/src/admin_api.py http://localhost:8080 team | cut -d' ' -f2)
python3 /root/src/client.py http://localhost:8080 team $TOKEN
