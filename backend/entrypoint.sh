#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations
# Use the config file explicitly for clarity
echo "Applying database migrations..."
alembic -c /app/alembic.ini upgrade head

echo "Migrations applied."

# Execute the command passed as arguments to this script (e.g., uvicorn)
echo "Starting application server..."
exec "$@"
