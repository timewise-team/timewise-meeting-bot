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
    rabbitmq-server \
    unzip \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome for Selenium (headless)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Install Chrome WebDriver
RUN CHROME_DRIVER_VERSION=`curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE` && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set up Selenium and other Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose necessary ports (e.g., RabbitMQ or the app)
EXPOSE 5672 15672

# Run RabbitMQ as a service, start meeting bot
CMD python main.py