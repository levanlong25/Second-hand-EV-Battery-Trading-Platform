from flask import Flask, jsonify, request, redirect, url_for, flash
from services.user_service import UserService

class UserController:
    @staticmethod
    def register(form = False):
        if form:
            email = request.form["email"]
            username = request.form["username"]
            password = request.form["password"]
        else:
            data = request.json
            email = data.get("email")
            username = data.get("username")
            password = data.get("password")
        user, status_code =  UserService.create_user(email, username, password)
        if isinstance(user, dict) and "error" in user:
            if form:
                flash(user["error"])
                return redirect(url_for("user_bp.login_form"))
            return jsonify(user), status_code
        if form:
            flash("Registration successful! Please login.")
            return redirect(url_for("user_bp.login_form"))
        return jsonify({
            "message": "User created successfully",
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }), status_code