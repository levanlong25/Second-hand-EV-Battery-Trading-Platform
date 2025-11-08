from app import create_app
from celery import Celery
import os
from celery.schedules import crontab # Import crontab

# Đọc cấu hình từ biến môi trường
broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
backend_url = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

# 1. Tạo Flask app
flask_app = create_app()

# 2. Tạo Celery app
celery_app = Celery(
    flask_app.import_name,
    broker=broker_url,
    backend=backend_url,
    include=['tasks']  # Trỏ đến file tasks.py
)
celery_app.conf.update(flask_app.config)

# Cấu hình Beat Schedule
celery_app.conf.beat_schedule = {
    'run-auction-tasks-every-minute': {
        'task': 'tasks.run_auction_tasks',  
        'schedule': crontab(minute='*'), # (SỬA) Dùng crontab(minute='*') cho chuẩn
    },
}
celery_app.conf.timezone = 'UTC'
 
class ContextTask(celery_app.Task):
    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return self.run(*args, **kwargs)

celery_app.Task = ContextTask