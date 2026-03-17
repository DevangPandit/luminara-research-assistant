FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

WORKDIR /app

# Copy and build frontend
COPY frontend/ ./frontend/
RUN cd frontend && npm install && npm run build

# Copy and install backend
COPY backend/ ./backend/
RUN pip install -r backend/requirements.txt

# Copy rest of project
COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]