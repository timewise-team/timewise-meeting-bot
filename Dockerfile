# Use Python 3.12 as the base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV CHROME_VERSION=130.0.6723.91
ENV CHROMEDRIVER_VERSION=130.0.6723.91

# Install necessary system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gnupg \
    build-essential \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libxtst6 \
    xdg-utils \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxi6 \
    unzip \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable=$CHROME_VERSION-1

# Download ChromeDriver that matches the Chrome version
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/130.0.6723.91/linux64/chrome-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set up Selenium and other Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Run RabbitMQ as a service, start Xvfb and the meeting bot
#CMD ["sh", "-c", "Xvfb :99 -ac 2>/dev/null & python main.py"]

CMD ["sh", "-c", "Xvfb :99 -screen 0 1920x1080x24 & sleep 3 && python main.py"]