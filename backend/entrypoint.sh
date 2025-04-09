#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Wait for DB --- #
MAX_TRIES=60
COUNT=0
echo "Waiting for database to be ready..."
while ! alembic -c /app/alembic.ini current > /dev/null 2>&1;
do
    COUNT=$(expr $COUNT + 1)
    if [ $COUNT -ge $MAX_TRIES ]; then
        echo "Database not ready after $MAX_TRIES tries. Exiting."
        exit 1
    fi
    echo "Attempt $COUNT/$MAX_TRIES: Database not ready, sleeping for 2 seconds..."
    sleep 2
done
echo "Database is ready."

# --- Run migrations --- #
# Use the config file explicitly for clarity
echo "Applying database migrations..."
alembic -c /app/alembic.ini upgrade head
echo "Migrations applied."

# --- Start application --- #
# Execute the command passed as arguments to this script (e.g., uvicorn)
echo "Starting application server..."
exec "$@"
