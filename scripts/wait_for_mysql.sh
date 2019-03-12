#!/bin/sh

# https://qiita.com/ry0f/items/6e29fa9f689b97058085
set -e

CMD="$@"

until mysqladmin ping -h db --silent; do
  echo 'Waiting for mysqld to be connectable...'
  sleep 5
done

echo "Command start"
exec $CMD
