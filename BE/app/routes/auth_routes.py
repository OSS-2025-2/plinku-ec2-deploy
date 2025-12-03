# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.config import db
from app.models.users import User
from flask import current_app
from flasgger import swag_from
import jwt
import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# JWT 생성
def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )
    return token


# 회원가입
@auth_bp.route("/signup", methods=["POST"])
@swag_from("../docs/auth_signup.yml")
def signup():
    data = request.get_json()

    if not data:
        return jsonify({"error": "요청 데이터가 필요합니다."}), 400

    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not email or not username or not password:
        return jsonify({"error": "email, username, password 필드는 필수입니다."}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "이미 존재하는 이메일입니다."}), 409

    hashed_pw = generate_password_hash(password)

    user = User(
        email=email,
        username=username,
        password_hash=hashed_pw
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "회원가입 성공", "user_id": user.id}), 201


# 로그인
@auth_bp.route("/login", methods=["POST"])
@swag_from("../docs/auth_login.yml")
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "이메일 또는 비밀번호가 잘못되었습니다."}), 401

    token = create_token(user.id)

    return jsonify({
        "message": "로그인 성공",
        "token": token,
        "user_id": user.id
    })


# 회원 탈퇴
@auth_bp.route("/delete", methods=["DELETE"])
@swag_from("../docs/auth_delete.yml")
def delete_user():
    data = request.get_json()
    user_id = data.get("user_id")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "존재하지 않는 사용자입니다."}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "회원 탈퇴 완료"}), 200
