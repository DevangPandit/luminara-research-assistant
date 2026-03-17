#!/bin/bash

# Install Node and build frontend
cd frontend
npm install
npm run build
cd ..

# Install Python dependencies
pip install -r backend/requirements.txt

# Start backend
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT