FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV POETRY_VIRTUALENVS_CREATE=False
# RUN poetry config virtualenvs.create false


ADD clientHook/ /app/clientHook/
ADD manage.py /app/manage.py
ADD pyproject.toml /app/pyproject.toml
ADD entrypoint.sh /app/entrypoint.sh

ADD staticfiles /app/staticfiles

# copy public key
ADD nginx/public.pem /app/public.pem
ENV TELEGRAM_PUBLIC_KEY=/app/public.pem

RUN pip install poetry
RUN poetry install  --no-dev --no-interaction --no-ansi

ENTRYPOINT ["bash", "/app/entrypoint.sh"]

EXPOSE 8000