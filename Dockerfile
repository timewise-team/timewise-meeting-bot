# Use the official Python image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    xvfb \
    ffmpeg \
    pulseaudio \
    wget \
    curl \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome browser
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update && apt-get install -y google-chrome-stable

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -q https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    rm chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/chromedriver

# Set up the Python environment
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Add user for running the bot securely
RUN useradd -m botuser && chown -R botuser /app
USER botuser

# Start the bot using xvfb to handle Selenium's headless mode with sound
CMD ["xvfb-run", "--auto-servernum", "--server-args='-screen 0 1280x1024x24'", "python", "-u", "bot.py"]

# Install RabbitMQ dependencies
RUN pip install pika

# Configure sounddevice (ensure your code correctly requests microphone permissions)
RUN pip install sounddevice

# Expose the port if RabbitMQ service requires it
EXPOSE 5672
