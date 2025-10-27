FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache /wheels/*

COPY . .

EXPOSE 5004

CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5004", "app:create_app()"]