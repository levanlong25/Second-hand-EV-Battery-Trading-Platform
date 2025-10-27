from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from services.pricing_service import PricingService
import logging

pricing_api = Blueprint('pricing_api', __name__, url_prefix='/api')
logger = logging.getLogger(__name__) 
pricing_service = PricingService()

@pricing_api.route('/suggest-price', methods=['POST'])
@jwt_required()  
def get_price_suggestion():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Thiếu JSON body"}), 400
    if not data.get('listing_type'):
         return jsonify({"error": "Thiếu 'listing_type' (vehicle hoặc battery)"}), 400

    try:
        suggested_price, explanation = pricing_service.suggest_price(data)

        if suggested_price is None: 
            return jsonify({"error": explanation}), 400
 
        return jsonify({
            "suggested_price": str(suggested_price),  
            "explanation": explanation
        }), 200

    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng tại suggest-price controller: {e}", exc_info=True)
        return jsonify({"error": "Lỗi máy chủ nội bộ."}), 500

