from app import db
 
class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
     
    listings = db.relationship('Listing', back_populates='seller')
    vehicles = db.relationship('Vehicle', back_populates='owner')
    batteries = db.relationship('Battery', back_populates='owner')
     
    reports = db.relationship('Report', back_populates='reporter')
    watchlist_items = db.relationship('WatchList', back_populates='user')

    def __repr__(self):
        return f'<User {self.username}>'