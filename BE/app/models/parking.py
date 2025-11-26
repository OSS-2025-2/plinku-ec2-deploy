#PLINKU_PROJECT/BE/app/models/parking.py
from app.config import db


class Parking(db.Model):
    __tablename__ = "parking"

    id = db.Column(db.Integer, primary_key=True)
    parking_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    price_per_hour = db.Column(db.Integer, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    distance_km = db.Column(db.Float, nullable=False)

    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)

    ev_charge = db.Column(db.Boolean, default=False)
    congestion = db.Column(db.String(20), nullable=True)
    type = db.Column(db.String(50), nullable=False)

    spots = db.relationship("ParkingSpot", backref="parking", lazy=True)
    buttons = db.relationship("ParkingButton", backref="parking", lazy=True)


class ParkingSpot(db.Model):
    __tablename__ = "parking_spot"

    id = db.Column(db.Integer, primary_key=True) # 기본 키
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"), nullable=False)# 주차장 ID
    spot_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)# 자리 상태 (available / occupied 등)
    color = db.Column(db.String(20), nullable=False)# UI 표시 색상
    ev_charge = db.Column(db.Boolean, default=False)

    # 자리 색상 설정 (주차장 타입에 따라 색 다르게)
    def set_color(self, parking):
        if self.status == "occupied":# 이미 사용 중이면 빨간색
            self.color = "red"
        else:# 해당 주차장이 EV 충전소면 파란색, 아니면 초록색
            self.color = "blue" if parking.ev_charge else "green"


class ParkingButton(db.Model):
    __tablename__ = "parking_buttons"

    id = db.Column(db.Integer, primary_key=True)
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"), nullable=False)# 주차장 ID
    reserve_button = db.Column(db.Boolean, default=False)  # 예약 버튼 표시 여부
    route_button = db.Column(db.Boolean, default=False)   # 경로 안내 버튼 표시 여부
