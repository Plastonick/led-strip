FROM python:3.8-slim

RUN apt update \
    && apt install -y --no-install-recommends gcc make build-essential scons swig \
    && pip3 install rpi-ws281x

RUN mkdir /data /app

COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "motion.py"]