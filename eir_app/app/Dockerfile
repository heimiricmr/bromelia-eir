FROM python:3.9-slim

RUN useradd eir

WORKDIR /home/eir

RUN apt-get update && apt-get install -y \
  libpq-dev \
  python-dev-is-python3 \
  && rm -rf /var/lib/apt/lists/*

COPY app.py config.py constants.py entrypoint.py models.py utils.py ./
COPY boot.sh config.yaml requirements.txt ./

RUN python -m venv venv
RUN venv/bin/pip install --upgrade pip setuptools wheel
RUN venv/bin/pip install -r requirements.txt

RUN chmod +x boot.sh
RUN chown -R eir:eir ./
USER eir

EXPOSE 3870
ENTRYPOINT ["./boot.sh"]