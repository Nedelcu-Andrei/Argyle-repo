FROM python:3.8 

WORKDIR /usr/src/argyle/

COPY . .

RUN apt-get update && apt-get install git && \
    pip install --upgrade pip setuptools && \
    pip install -r requirements.txt && \
    apt-get install -y \
        curl \
        unzip \
        libgbm-dev \
        libx11-xcb1 \
        libxcomposite1 \
        libxcursor1 \
        libxdamage1 \
        libxi6 \
        libxtst6 \
        libnss3 \
        libcups2 \
        libxss1 \
        libxrandr2 \
        libasound2 \
        libpangocairo-1.0-0 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libgtk-3-0 

RUN pip install playwright && \
    playwright install

CMD ["python", "main.py"]
