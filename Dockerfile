FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn

RUN addgroup --system django && adduser --system --ingroup django django

COPY . /app

RUN chown -R django:django /app
RUN chmod +x /app/entrypoint.sh

USER django

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--config", "deploy/gunicorn/gunicorn.conf.py", "config.wsgi:application"]

