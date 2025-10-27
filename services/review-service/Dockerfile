FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5005
CMD ["gunicorn", "--bind", "0.0.0.0:5005", "app:create_app()"]
