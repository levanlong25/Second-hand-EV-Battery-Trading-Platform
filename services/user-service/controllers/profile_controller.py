from flask import request, jsonify, Blueprint, flash, redirect, render_template, url_for, session
from services.profile_service import ProfileService  

profile_site = Blueprint("profile_site", __name__)

class ProfileController: 
    @profile_site.route("/profile", methods=["GET"])
    def get_profile():      
        user_id = session.get('user_id') 
        if not user_id:
            flash("Vui lòng đăng nhập để xem hồ sơ.", "error")
            return redirect(url_for("auth_site.login_form")) 
        profile = ProfileService.get_profile_by_user_id(user_id) 
        if not profile: 
            flash("Không tìm thấy dữ liệu hồ sơ.", "error") 
            return redirect(url_for("profile_site.update_profile_form"))  
        if request.accept_mimetypes.accept_json and \
           not request.accept_mimetypes.accept_html:
            return jsonify({ 
                "user_id": profile.user_id,
                "full_name": profile.full_name,
                "phone_number": profile.phone_number,
                "address": profile.address,
                "bio": profile.bio,
                "avatar_url": profile.avatar_url
            }), 200
        else: 
            return render_template("profile.html", profile=profile)
 
    @profile_site.route("/profile_update", methods = ["GET"])
    def update_profile_form():
        user_id = session.get('user_id')
        if not user_id:
            flash("Vui lòng đăng nhập để cập nhật hồ sơ.", "error")
            return redirect(url_for("auth_site.login_form")) 
        profile = ProfileService.get_profile_by_user_id(user_id) 
        return render_template("update_profile.html", profile=profile)
 
    @profile_site.route("/profile_update", methods=["POST"])
    def update_profile(): 
        user_id = session.get('user_id')
        if not user_id:
            flash("Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.", "error")
            return redirect(url_for("auth_site.login_form"))
        new_fullname = request.form.get("new_fullname")
        new_phone_number = request.form.get("new_phone_number")
        new_address = request.form.get("new_address")
        new_bio = request.form.get("new_bio") 
        result = ProfileService.update_profile(
            user_id, 
            new_fullname=new_fullname, 
            new_phone_number=new_phone_number, 
            new_address=new_address, 
            new_bio=new_bio
        )

        if "error" in result:
            flash(result["error"], "error")
            return redirect(url_for("profile_site.update_profile_form"))
            
        flash(result["message"], "success")
        return redirect(url_for("profile_site.get_profile"))  
    @profile_site.route("/update_avatar", methods=["POST"])
    def update_avatar():
        user_id = session.get('user_id')
        if not user_id:
            flash("Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.", "error")
            return redirect(url_for("auth_site.login_form")) 
        if 'avatar' not in request.files:
            flash("Không tìm thấy file avatar.", "error")
            return redirect(url_for("profile_site.update_profile_form")) 
        avatar_file = request.files['avatar'] 
        if avatar_file.filename == '':
            flash("Không có file nào được chọn.", "error")
            return redirect(url_for("profile_site.update_profile_form")) 
        new_avatar_url = f"/uploads/avatars/{user_id}/{avatar_file.filename}"  
        result = ProfileService.update_avatar(user_id, new_avatar_url) 
        if "error" in result:
            flash(result["error"], "error")
            return redirect(url_for("profile_site.update_profile_form")) 
        flash(result["message"], "success")
        return redirect(url_for("profile_site.get_profile")) 
