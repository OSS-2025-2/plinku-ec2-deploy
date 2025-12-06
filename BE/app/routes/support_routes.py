from flask import Blueprint, request, jsonify, g
from app.config import db
from app.models.community import Contact
from app.routes.auth_utils import login_required
from flasgger import swag_from


support_bp = Blueprint("support", __name__, url_prefix="/api/support")


# 문의 등록
# POST /api/support/contact
# body: { "message": "..." }
@support_bp.route("/contact", methods=["POST"])
@swag_from("../docs/support_contact.yml")
@login_required
def submit_contact():
    data = request.get_json() or {}
    message = data.get("message")

    if not message:
        return jsonify({"error": "message는 필수입니다."}), 400

    contact = Contact(
        user_id=g.current_user_id,
        message=message
    )
    db.session.add(contact)
    db.session.commit()

    return jsonify({"message": "문의가 접수되었습니다."}), 201
