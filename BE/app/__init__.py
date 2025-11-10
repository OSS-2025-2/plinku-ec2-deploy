from flask import Flask

def create_app():
    app = Flask(__name__)

    # 나중에 기능이 생기면 여기에 등록
    # 예시:
    # from app.routes.parking_routes import parking_bp
    # app.register_blueprint(parking_bp)

    @app.route('/')
    def home():
        return "서버가 정상적으로 실행 중입니다!"

    return app