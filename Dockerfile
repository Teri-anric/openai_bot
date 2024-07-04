FROM python:3.11-slim

RUN mkdir /app
WORKDIR /app


ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV POETRY_VIRTUALENVS_CREATE=False
#&& poetry config virtualenvs.create false


ADD clientHook/ /app/clientHook/
ADD manage.py /app/manage.py
ADD pyproject.toml /app/pyproject.toml

RUN pip install poetry
RUN poetry install  --no-dev --no-interaction --no-ansi

ENTRYPOINT ["uvicorn", "clientHook.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000