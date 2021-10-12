FROM python:3.9-slim

RUN useradd eir

WORKDIR /home/eir

RUN apt-get update && apt-get install -y \
  libpq-dev \
  python-dev \
  && rm -rf /var/lib/apt/lists/*

RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install psycopg2-binary==2.9.1
RUN venv/bin/pip install pyyaml==5.4.1
RUN venv/bin/pip install sqlalchemy==1.4.25
RUN venv/bin/pip install bromelia==0.2.0

COPY * ./
RUN chmod +x boot.sh

RUN chown -R eir:eir ./
USER eir

EXPOSE 3870
ENTRYPOINT ["./boot.sh"]