FROM python:3.6-slim

ENV PYTHONUNBUFFERED 1
RUN mkdir /proj
WORKDIR /proj
COPY /src/constraints.txt /proj/src/
COPY /src/requirements.txt /proj/src/

RUN pip install --upgrade pip\
    && apt-get update\
    && apt-get install -y mysql-client \
        default-libmysqlclient-dev \
        build-essential \
        python3-dev \
    && pip install -r src/requirements.txt\
    && rm -rf ~/.cache/pip \
    && rm -rf /var/lib/apt/lists/*

COPY . /proj/

CMD python3
