#!/bin/bash

# Development mode
if [ "$1" = "dev" ]; then
    python wsgi.py
# Production mode
else
    gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
fi
