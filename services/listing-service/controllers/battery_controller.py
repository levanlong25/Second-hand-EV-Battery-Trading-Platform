from flask import Blueprint, request, jsonify
from services.battery_service import BatteryService

battery_bp = Blueprint("battery_bp", __name__)

# Thêm pin mới
@battery_bp.route("/batteries/add", methods=["POST"])
def add_battery():
    data = request.get_json()
    listing_id = data.get("listing_id")
    capacity_kwh = data.get("capacity_kwh")
    health_percent = data.get("health_percent")
    manufacturer = data.get("manufacturer")

    if not all([listing_id, capacity_kwh, health_percent, manufacturer]):
        return jsonify({"error": "Missing required fields"}), 400

    result = BatteryService.addBattery(listing_id, capacity_kwh, health_percent, manufacturer)
    return jsonify(result)

# Cập nhật thông tin pin
@battery_bp.route("/batteries/update/<int:battery_id>", methods=["PUT"])
def update_battery(battery_id):
    data = request.get_json()
    capacity_kwh = data.get("capacity_kwh")
    health_percent = data.get("health_percent")

    result = BatteryService.updateBatteryStatus(battery_id, capacity_kwh, health_percent)
    return jsonify(result)

# Lấy danh sách tất cả pin
@battery_bp.route("/batteries", methods=["GET"])
def get_all_batteries():
    result = BatteryService.get_all_batteries()
    return jsonify(result)

# Lấy thông tin pin theo ID
@battery_bp.route("/batteries/<int:battery_id>", methods=["GET"])
def get_battery_by_id(battery_id):
    result = BatteryService.get_battery_by_id(battery_id)
    return jsonify(result)

# Lấy pin theo listing_id
@battery_bp.route("/batteries/listing/<int:listing_id>", methods=["GET"])
def get_batteries_by_listing(listing_id):
    result = BatteryService.get_batteries_by_listing(listing_id)
    return jsonify(result)

# Xóa pin
@battery_bp.route("/batteries/delete/<int:battery_id>", methods=["DELETE"])
def delete_battery(battery_id):
    result = BatteryService.delete_battery(battery_id)
    return jsonify(result)