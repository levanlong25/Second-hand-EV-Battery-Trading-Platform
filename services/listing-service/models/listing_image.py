from app import db

class ListingImage(db.Model):
    __tablename__ = 'listing_image'

    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listing.listing_id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    listing = db.relationship('Listing', back_populates='images')

    def __repr__(self):
        return f"<ListingImage {self.image_url} (ID: {self.image_id})>"