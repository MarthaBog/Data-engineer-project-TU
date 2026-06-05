FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      cron \
      bash \
      git \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dbt
COPY dbt-requirements.txt .
RUN pip install --no-cache-dir -r dbt-requirements.txt

COPY orchestrator/run.sh /app/orchestrator/run.sh
RUN chmod +x /app/orchestrator/run.sh

COPY orchestrator/crontab /etc/cron.d/orchestrator
RUN chmod 0644 /etc/cron.d/orchestrator \
    && crontab /etc/cron.d/orchestrator \
    && mkdir -p /var/log \
    && touch /var/log/orchestrator.log

CMD ["cron", "-f"]
