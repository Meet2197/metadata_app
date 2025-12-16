FROM openjdk:17.0.2-jdk-slim-bullseye

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files
COPY ./app /app/app
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

# Run Python app in module mode
CMD ["python3", "-m", "app.main"]
