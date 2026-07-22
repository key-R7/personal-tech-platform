FROM python:3.12.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/django

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

RUN addgroup --system django \
    && adduser --system --home /home/django --ingroup django django \
    && mkdir -p /home/django \
    && mkdir -p /app/staticfiles \
    && chown -R django:django /home/django /app/staticfiles

COPY --chown=django:django . .
RUN chmod +x /app/docker/entrypoint.sh

USER django

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-"]
