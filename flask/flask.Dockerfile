FROM python:3.8-slim

RUN apt update \
    && pip3 install flask

EXPOSE 5000

RUN mkdir /data
COPY . .
ENTRYPOINT ["flask", "run", "--host", "0.0.0.0"]