import random
from app import create_app
from app.config import db
from app.models.parking import Parking, ParkingSpot

app = create_app()

SPOTS_PER_PARKING = 100
EV_RATIO = 0.1   # 전체 자리 중 10%를 EV 충전소로 만들기

with app.app_context():
    parkings = Parking.query.all()

    for p in parkings:
        print(f"{p.parking_name} 더미 생성 중...")

        existing = ParkingSpot.query.filter_by(parking_id=p.id).count()
        if existing > 0:
            print(f"이미 {existing}개 존재 → 스킵")
            continue

        # 🔥 EV 충전소 자리를 랜덤으로 선택
        ev_spot_count = int(SPOTS_PER_PARKING * EV_RATIO)
        ev_spots = set(random.sample(range(1, SPOTS_PER_PARKING + 1), ev_spot_count))

        for i in range(1, SPOTS_PER_PARKING + 1):

            is_ev = i in ev_spots     # 랜덤 EV 자리

            status = "available"
            color = "blue" if is_ev else "green"  # available 상태 기준 색상

            spot = ParkingSpot(
                parking_id=p.id,
                spot_id=i,
                status=status,
                color=color,
                ev_charge=is_ev
            )
            db.session.add(spot)

        # 🔥 주차장 자체의 ev_charge는 EV 자리가 1개라도 있으면 True
        p.ev_charge = len(ev_spots) > 0

        db.session.commit()
        print(f"==> {p.parking_name}: EV {len(ev_spots)}개 생성 완료")
