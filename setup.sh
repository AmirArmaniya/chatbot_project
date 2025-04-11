#!/bin/bash

# Setup script for Multi-Tenant Farsi Chatbot
# This script creates necessary directories and initializes the project

set -e  # Exit on error

echo "Starting setup for Multi-Tenant Farsi Chatbot..."

# Create directory structure
mkdir -p rasa
mkdir -p flask
mkdir -p data
mkdir -p models
mkdir -p logs

# Generate tenant data
echo "Generating tenant data..."
cd data
python generate_tenants.py
cd ..

# Build Docker images
echo "Building Docker images..."
docker-compose build

# Train Rasa model
echo "Training Rasa model..."
docker-compose run --rm rasa train --domain domain.yml --data data --out models

echo "Setup completed successfully!"
echo "To start the services, run: docker-compose up -d"
echo "To check the status, run: docker-compose ps"