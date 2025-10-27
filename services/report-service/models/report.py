from app import db
from datetime import datetime, timezone

class Report(db.Model):
    __tablename__ = 'reports'  

    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reporter_id = db.Column(db.Integer, nullable=False)  
    transaction_id = db.Column(db.Integer, nullable=False)  
    reported_user_id = db.Column(db.Integer, nullable=False)  
    reason = db.Column(db.String(100), nullable=False)  
    details = db.Column(db.String(500), nullable=True)  
    status = db.Column(db.Enum('pending', 'resolved', 'dismissed', name='report_status_enum'), default='pending', nullable=False)  
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  


    def __repr__(self):
        return f"<Report {self.report_id} - TXN:{self.transaction_id} - Reporter:{self.reporter_id} -> Reported:{self.reported_user_id} - Status:{self.status}>"