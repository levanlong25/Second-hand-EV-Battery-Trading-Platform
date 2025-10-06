from flask import (
    Blueprint, request, jsonify, render_template,
    redirect, url_for, flash, session
)
from services.listing_service import ListingService

# Khởi tạo Blueprint cho Listing
listing_site = Blueprint("listing_site", __name__)

class ListingController:
    # Trang hiển thị tất cả listing
    @listing_site.route("/listings", methods=["GET"])
    def list_all():
        listings = ListingService.get_all_listings()

        # Nếu client yêu cầu JSON
        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            serialized = [ListingService.serialize_listing(l) for l in listings]
            return jsonify(serialized), 200

        # Mặc định trả về HTML
        return render_template("listings.html", listings=listings)

    # Xem chi tiết 1 listing
    @listing_site.route("/listings/<int:listing_id>", methods=["GET"])
    def get_listing(listing_id):
        listing = ListingService.get_listing_by_id(listing_id)
        if not listing:
            flash("Không tìm thấy bài đăng.", "error")
            return redirect(url_for("listing_site.list_all"))

        if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
            return jsonify(ListingService.serialize_listing(listing)), 200

        return render_template("listing_detail.html", listing=listing)

    # Form tạo mới listing
    @listing_site.route("/listing_create", methods=["GET"])
    def create_form():
        user_id = session.get("user_id")
        if not user_id:
            flash("Vui lòng đăng nhập để đăng bài.", "error")
            return redirect(url_for("auth_site.login_form"))
        return render_template("create_listing.html")

    # Xử lý tạo mới listing
    @listing_site.route("/listing_create", methods=["POST"])
    def create_listing():
        user_id = session.get("user_id")
        if not user_id:
            flash("Phiên làm việc đã hết hạn. Vui lòng đăng nhập lại.", "error")
            return redirect(url_for("auth_site.login_form"))

        try:
            data = {
                "seller_id": user_id,
                "type": request.form.get("type"),
                "title": request.form.get("title"),
                "description": request.form.get("description"),
                "price": float(request.form.get("price") or 0),
            }

            result = ListingService.create_listing(data)
            if not result:
                flash("Không thể tạo bài đăng. Vui lòng thử lại.", "error")
                return redirect(url_for("listing_site.create_form"))

            flash("Đăng bài thành công!", "success")
            return redirect(url_for("listing_site.list_all"))
        except Exception as e:
            flash(f"Lỗi khi tạo bài đăng: {str(e)}", "error")
            return redirect(url_for("listing_site.create_form"))

    # Form cập nhật listing
    @listing_site.route("/listing_update/<int:listing_id>", methods=["GET"])
    def update_form(listing_id):
        listing = ListingService.get_listing_by_id(listing_id)
        if not listing:
            flash("Không tìm thấy bài đăng.", "error")
            return redirect(url_for("listing_site.list_all"))
        return render_template("update_listing.html", listing=listing)

    # Xử lý cập nhật listing
    @listing_site.route("/listing_update/<int:listing_id>", methods=["POST"])
    def update_listing(listing_id):
        listing = ListingService.get_listing_by_id(listing_id)
        if not listing:
            flash("Không tìm thấy bài đăng.", "error")
            return redirect(url_for("listing_site.list_all"))

        try:
            data = {
                "type": request.form.get("type"),
                "title": request.form.get("title"),
                "description": request.form.get("description"),
                "price": float(request.form.get("price") or 0),
                "status": request.form.get("status"),
            }

            updated = ListingService.update_listing(listing_id, data)
            if not updated:
                flash("Cập nhật thất bại.", "error")
                return redirect(url_for("listing_site.update_form", listing_id=listing_id))

            flash("Cập nhật thành công!", "success")
            return redirect(url_for("listing_site.get_listing", listing_id=listing_id))
        except Exception as e:
            flash(f"Lỗi khi cập nhật: {str(e)}", "error")
            return redirect(url_for("listing_site.update_form", listing_id=listing_id))

    # Xóa listing
    @listing_site.route("/listing_delete/<int:listing_id>", methods=["POST"])
    def delete_listing(listing_id):
        listing = ListingService.get_listing_by_id(listing_id)
        if not listing:
            flash("Không tìm thấy bài đăng để xóa.", "error")
            return redirect(url_for("listing_site.list_all"))

        try:
            success = ListingService.delete_listing(listing_id)
            if success:
                flash("Xóa bài đăng thành công!", "success")
            else:
                flash("Xóa thất bại. Vui lòng thử lại.", "error")
        except Exception as e:
            flash(f"Lỗi khi xóa: {str(e)}", "error")

        return redirect(url_for("listing_site.list_all"))
