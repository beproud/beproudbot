FROM ubuntu:16.04

# 基本的な設定
RUN apt update -y && apt install -y wget python3 sqlite3
RUN wget -O- https://bootstrap.pypa.io/get-pip.py | python3
RUN cp /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# アプリの依存
COPY ./constraints.txt /tmp
COPY ./requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python
