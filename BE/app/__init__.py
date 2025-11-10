from flask import Flask
# from app.routes.parking_routes import parking_bp
from app.routes.parking_routes import parking_bp

def create_app():
    app = Flask(__name__)
    # 나중에 기능이 생기면 여기에 등록
    # 예시:
    # app.register_blueprint(parking_bp)
    app.register_blueprint(parking_bp)
    return app