#!/bin/bash
# Initialize project: copy .env.example to .env if .env doesn't exist

if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo ".env created successfully"
else
  echo ".env already exists"
fi
