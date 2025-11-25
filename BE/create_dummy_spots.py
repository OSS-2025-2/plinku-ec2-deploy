# PLINKU_PROJECT/BE/create_dummy_spots.py
from app import create_app
from app.config import db
from app.models.parking import Parking, ParkingSpot

app = create_app()

# 🔥 자리 개수
SPOTS_PER_PARKING = 100

with app.app_context():

    # 전체 주차장 가져오기
    parkings = Parking.query.all()

    for p in parkings:
        print(f"주차장 {p.id} - {p.parking_name} 더미 생성 중...")

        # 이미 자리 있으면 건너뛰기
        existing = ParkingSpot.query.filter_by(parking_id=p.id).count()
        if existing > 0:
            print(f"이미 {existing}개 존재 → 스킵")
            continue

        # 자리 생성
        for i in range(1, SPOTS_PER_PARKING + 1):
            status = "available"  # 처음엔 모두 비어있음
            color = "green" if not p.ev_charge else "blue"

            spot = ParkingSpot(
                parking_id=p.id,
                spot_id=i,
                status=status,
                color=color
            )
            db.session.add(spot)

        db.session.commit()
        print(f"==> 주차장 {p.id}에 {SPOTS_PER_PARKING}개 생성 완료!")

print("🎉 모든 주차장 더미 데이터 생성 완료!")
