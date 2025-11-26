 #PLINKU_PROJECT/BE/app/__init__.py
from flask import Flask
from app.config import db
from app.routes.parking_routes import parking_bp
from flasgger import Swagger
from app.models.parking import Parking, ParkingSpot, ParkingButton
import os
def create_app():
    app = Flask(__name__)

    # DB 설정
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 🔥 SQLAlchemy 앱과 연결 (필수)
    db.init_app(app)

    db_path = os.path.join(os.getcwd(), "parking.db")
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ 기존 parking.db 삭제됨 → 새로 생성 예정")

    # Swagger 설정
    swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Parking API",
            "description": "API 문서",
            "version": "1.0.0"
        }
    }

    Swagger(app, config=swagger_config, template=swagger_template)

    # DB 테이블 생성
    with app.app_context():
        db.create_all()

    # Blueprint 등록
    app.register_blueprint(parking_bp)

    # 🔥 반드시 return app 해야 함
    return app
