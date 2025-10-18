from app import db
from models.listing import Listing
from models.vehicle import Vehicle
from models.battery import Battery

class ComparisonService:

    @staticmethod
    def get_comparison_data(listing_ids):
        if not listing_ids or not isinstance(listing_ids, list):
            return None, [], "No listing IDs provided."
        listings = Listing.query.filter(
            Listing.listing_id.in_(listing_ids)
        ).all()

        if not listings:
            return None, [], "No valid listings found for the given IDs."
 
        first_listing_type = listings[0].listing_type
        if not all(l.listing_type == first_listing_type for l in listings):
            return None, [], "Cannot compare items of different types (vehicles and batteries)."

        comparison_type = first_listing_type
        comparison_data = []
 
        try:
            for listing in listings:
                item_data = {
                    "listing_id": listing.listing_id,
                    "title": listing.title,
                    "price": listing.price,
                    "status": listing.status,
                    "created_at": listing.created_at
                }

                if comparison_type == 'vehicle': 
                    vehicle = listing.vehicle 
                    if vehicle:
                        item_data.update({
                            "item_id": vehicle.vehicle_id,
                            "brand": vehicle.brand,
                            "model": vehicle.model,
                            "year": vehicle.year,
                            "mileage": vehicle.mileage 
                        })
                
                elif comparison_type == 'battery': 
                    battery = listing.battery
                    if battery:
                        item_data.update({
                            "item_id": battery.battery_id,
                            "capacity_kwh": battery.capacity_kwh,
                            "health_percent": battery.health_percent,
                            "manufacturer": battery.manufacturer 
                        })
                
                comparison_data.append(item_data)
 
            id_order = {id: i for i, id in enumerate(listing_ids)}
            comparison_data.sort(key=lambda x: id_order.get(x['listing_id'], float('inf')))

            return comparison_type, comparison_data, "Comparison data retrieved successfully."

        except Exception as e: 
            print(f"Error in get_comparison_data: {e}")
            return None, [], f"An internal error occurred: {str(e)}"