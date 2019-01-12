FROM python:3.6-alpine

RUN apk --no-cache add -q gcc linux-headers build-base

COPY requirements.txt /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /code

ADD . /code

ENTRYPOINT ["python", "main.py"]
