FROM python:3.11-slim

# Install wkhtmltopdf and dependencies
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create virtual display for wkhtmltopdf
ENV DISPLAY=:99

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "Xvfb :99 -screen 0 1024x768x24 & python bot.py"]
