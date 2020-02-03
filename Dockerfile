FROM python:3.7

RUN mkdir /app

COPY ./requirements.txt /app/requirements.txt

RUN pip3 install -r /app/requirements.txt

RUN mkdir -p /app

COPY ./ /app/

ENV TELEGRAM_KEY=$TELEGRAM_KEY

WORKDIR /app

RUN mkdir /data

EXPOSE 1080

VOLUME ["/app/data"]

CMD python main.py
