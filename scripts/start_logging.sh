#!/bin/bash

cd "$(dirname "$0")/.."

LOG_PID=`ps -ef | grep "docker-compose logs" | grep -v "grep" | awk '{print $2}'`

if [ -z "$LOG_PID" ];then
  echo "Not found logging pid."
else
  kill -9 $LOG_PID
fi

nohup sh -c "docker-compose logs --no-color -f | python3 scripts/logfilter.py" &
