FROM python:3.8-slim

RUN apt update \
    && apt install -y --no-install-recommends gcc make build-essential scons swig \
    && pip3 install --no-cache-dir --no-input rpi-ws281x \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /data /app

COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "motion.py"]