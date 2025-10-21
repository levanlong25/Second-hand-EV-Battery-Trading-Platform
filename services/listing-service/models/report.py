from app import db

class Report(db.Model):
    __tablename__ = 'report'

    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reporter_id = db.Column(db.Integer, nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.listing_id'), nullable=False)
    report_type = db.Column(db.Enum('seller', 'transaction', 'listing', 'other', name='report_type_enum'), nullable=False)
    
    listing = db.relationship('Listing', back_populates='reports') 
    
    def __repr__(self):
        return f"<Report {self.report_id} on Listing {self.listing_id}>"