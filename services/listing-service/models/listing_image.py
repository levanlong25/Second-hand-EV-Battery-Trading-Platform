from app import db

class ListingImage(db.Model):
    __tablename__ = 'listing_images'

    image_id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.listing_id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
     
    listing = db.relationship('Listing', back_populates='images')

    def __repr__(self):
        return f'<ListingImage {self.image_id} for Listing {self.listing_id}>'
