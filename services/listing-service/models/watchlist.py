from app import db

class WatchList(db.Model):
    __tablename__ = 'watchlist'

    watchlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.listing_id'), nullable=False)

    listing = db.relationship('Listing', back_populates='watchlists') 

    def __repr__(self):
        return f"<WatchList {self.watchlist_id} - User {self.user_id} - Listing {self.listing_id}>"