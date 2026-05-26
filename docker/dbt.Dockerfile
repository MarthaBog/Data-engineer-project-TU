FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/app

COPY dbt-requirements.txt .
RUN pip install --no-cache-dir -r dbt-requirements.txt

ENTRYPOINT ["dbt"]
