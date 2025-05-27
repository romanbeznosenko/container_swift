#!/bin/bash
# wait-for-mongodb.sh

set -e

host="$1"
shift
cmd="$@"

until mongosh --host "$host" --username root --password rootpassword --authenticationDatabase admin --eval "db.adminCommand('ismaster')" --quiet; do
  >&2 echo "MongoDB is unavailable - sleeping"
  sleep 2
done

>&2 echo "MongoDB is up - executing command"
exec $cmd