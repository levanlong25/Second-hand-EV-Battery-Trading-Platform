from flask import request, redirect, url_for, flash, render_template, Blueprint, session
from services.user_service import UserService
from models.user import User
from app import db, r
import os
import jwt

SECRET_KEY = "081025"
ADMIN_SERVICE_URL = "http://admin-service:5000"

auth_site = Blueprint("auth_site", __name__)

class UserController:

    @auth_site.route("/register", methods=["GET"])
    def register_form():
        return render_template("register.html")

    @auth_site.route("/register", methods=["POST"])
    def register():
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        user = UserService.register(email, username, password)
        if isinstance(user, dict) and "error" in user:
            flash(user["error"])
            return redirect(url_for("auth_site.register_form"))
        return redirect(url_for("auth_site.login_form"))

    @auth_site.route("/login", methods=["GET"])
    def login_form():
        return render_template("login.html")

    @auth_site.route("/login", methods=["POST"])
    def login():
        email_username = request.form["email_username"]
        password = request.form["password"]
        remember_me = request.form.get("remember_me")
        login_result = UserService.login(email_username, password)
        if isinstance(login_result, dict) and "error" in login_result:
            flash(login_result["error"])
            return redirect(url_for("auth_site.login_form"))
        user = login_result
        session['user_id'] = user.user_id
        if remember_me:
            r.setex(f"remember:{user.user_id}", 60*60*24*7, "remembered")
        if user.role == "admin":
            flash(f"Chào mừng quản trị viên {user.username}!", "success")
            return redirect(f"{ADMIN_SERVICE_URL}/dashboard")
        flash(f"Đăng nhập thành công! Chào mừng {user.username}.")
        return redirect(url_for("profile_site.get_profile"))

    @auth_site.route("/forget-password", methods=["GET"])
    def forget_password_form():
        return render_template("forget_password.html")

    @auth_site.route("/send-otp", methods=["POST"])
    def send_reset_otp_form():
        email = request.form["email"]
        result = UserService.send_reset_otp(email)
        if "error" in result:
            flash(result["error"])
        else:
            flash(result["message"])
        return redirect(url_for("auth_site.forget_password_form", email=email))

    @auth_site.route("/reset-password", methods=["POST"])
    def reset_password_form():
        email = request.form["email"]
        input_otp = request.form["input_otp"]
        new_password = request.form["new_password"]
        result = UserService.forget_password(email, input_otp, new_password)
        if "error" in result:
            flash(result["error"])
            return redirect(url_for("auth_site.forget_password_form"))
        flash(result["message"])
        return redirect(url_for("auth_site.login_form"))

    @auth_site.route("/update", methods=["GET"])
    def update_form():
        return render_template("change_information.html")

    @auth_site.route("/update", methods=["POST"])
    def update():
        user_id = request.form["user_id"]
        new_username = request.form["new_username"]
        new_password = request.form["new_password"]
        result = UserService.update_by_member(user_id, new_username, new_password)
        if "error" in result:
            flash(result["error"])
            return redirect(url_for("auth_site.login_form"))
        flash(result["message"])
        return redirect(url_for("auth_site.profile"))

    @auth_site.route("/delete", methods=["POST"])
    def delete():
        user_id = request.form["user_id"]
        result = UserService.delete_user_by_id(user_id)
        if "error" in result:
            flash(result["error"])
            return redirect(url_for("auth_site.register_form"))
        flash(result["message"])
        return redirect(url_for("auth_site.login_form"))
