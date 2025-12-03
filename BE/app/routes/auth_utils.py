import jwt
from functools import wraps
from flask import request, jsonify, current_app, g
from flasgger import swag_from


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization 헤더에 Bearer 토큰이 필요합니다."}), 401

        token = auth_header.split(" ", 1)[1]

        try:
            payload = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "토큰이 만료되었습니다."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401

        # 현재 로그인한 유저 ID를 전역 컨텍스트에 저장
        g.current_user_id = payload.get("user_id")
        if g.current_user_id is None:
            return jsonify({"error": "토큰에 user_id가 없습니다."}), 401

        return f(*args, **kwargs)

    return wrapper
