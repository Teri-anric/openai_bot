python manage.py migrate --noinput

uvicorn clientHook.asgi:application --host 0.0.0.0 --port 8000