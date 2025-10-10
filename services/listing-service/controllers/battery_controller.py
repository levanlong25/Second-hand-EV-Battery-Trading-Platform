from flask import Blueprint, request, jsonify, flash, render_template, redirect, url_for
from services.battery_service import BatteryService

battery_bp = Blueprint("battery_bp", __name__)

# =========================
# Thêm pin mới
# =========================
@battery_bp.route("/batteries/add", methods=["POST"])
def add_battery():
    capacity_kwh = request.form.get("capacity_kwh")
    health_percent = request.form.get("health_percent")
    manufacturer = request.form.get("manufacturer")

    # Kiểm tra dữ liệu
    if not all([capacity_kwh, health_percent, manufacturer]):
        flash("Missing required fields", "error")
        return redirect(url_for("battery_bp.show_add_form"))

    battery = BatteryService.addBattery(
        capacity_kwh=capacity_kwh,
        health_percent=health_percent,
        manufacturer=manufacturer
    )

    if "error" in battery:
        flash(battery["error"], "error")
        return redirect(url_for("battery_bp.show_add_form"))

    flash("Battery added successfully", "success")
    return redirect(url_for("battery_bp.get_all_batteries"))


# =========================
# Cập nhật thông tin pin
# =========================
@battery_bp.route("/batteries/update/<int:battery_id>", methods=["POST"])
def update_battery(battery_id):
    capacity_kwh = request.form.get("capacity_kwh")
    health_percent = request.form.get("health_percent")

    if not all([capacity_kwh, health_percent]):
        flash("Missing required fields", "error")
        return redirect(url_for("battery_bp.get_all_batteries"))

    result = BatteryService.updateBatteryStatus(
        battery_id,
        capacity_kwh=capacity_kwh,
        health_percent=health_percent
    )

    if "error" in result:
        flash(result["error"], "error")
        return redirect(url_for("battery_bp.get_all_batteries"))

    flash("Battery updated successfully", "success")
    return redirect(url_for("battery_bp.get_all_batteries"))


# =========================
# Lấy danh sách tất cả pin
# =========================
@battery_bp.route("/batteries", methods=["GET"])
def get_all_batteries():
    result = BatteryService.get_all_batteries()
    return render_template("batteries/list.html", batteries=result)


# =========================
# Trang thêm pin (form)
# =========================
@battery_bp.route("/batteries/add", methods=["GET"])
def show_add_form():
    return render_template("batteries/add.html")
