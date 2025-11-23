import os
from flask import current_app
from flask import Blueprint, request, jsonify
from app.models.parking import Parking, ParkingSpot
from app.models.reservations import Reservation
from datetime import datetime
from flasgger import swag_from

from app.config import db

reservation_bp = Blueprint("reservations", __name__)

@reservation_bp.route("/api/reservations", methods=["POST"])
@swag_from("../docs/reservation_create.yml")
def create_reservation():
    data = request.get_json()

    user_id = data.get("user_id")
    parking_id = data.get("parking_id")
    spot_id = data.get("spot_id")

    # 🔥 문자열 → datetime 변환
    
    start_time = datetime.fromisoformat(data.get("start_time"))
    end_time = datetime.fromisoformat(data.get("end_time"))

    if not all([user_id, parking_id, spot_id, start_time, end_time]):
        return jsonify({"status": "fail", "message": "Missing required fields"}), 400

    spot = ParkingSpot.query.get(spot_id)
    if not spot or spot.status != "available":
        return jsonify({"status": "fail", "message": "Spot is unavailable"}), 400

    parking = Parking.query.get(parking_id)

    reservation = Reservation(
        user_id=user_id,
        parking_id=parking_id,
        spot_id=spot_id,
        start_time=start_time,
        end_time=end_time
    )
    db.session.add(reservation)

    # 자리 상태 변경
    spot.status = "unavailable"
    spot.color = "red"

    # 주차장 카운트 감소
    parking.available_spots -= 1

    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "주차장 예약이 완료되었습니다.",
        "data": {
            "type": "parking",
            "reservation_id": reservation.id,
            "user_id": user_id,
            "parking_id": parking_id,
            "parking_name": parking.parking_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "price_per_hour": parking.price_per_hour,
            "total_price": parking.price_per_hour * 1,
            "buttons": {
                "cancel": True,
                "route": True
            }
        }
    })



@reservation_bp.route("/api/reservations/<int:id>", methods=["DELETE"])
@swag_from("../docs/reservation_cancel.yml")
def cancel_reservation(id):
    reservation = Reservation.query.get(id)

    if not reservation:
        return jsonify({"status": "fail", "message": "예약을 취소할 수 없습니다."}), 404

    # 자리 및 주차장 복구
    spot = ParkingSpot.query.get(reservation.spot_id)
    parking = Parking.query.get(reservation.parking_id)

    spot.status = "available"
    spot.color = "green"
    parking.available_spots += 1

    reservation.status = "cancelled"
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "주차장 예약이 취소되었습니다.",
        "data": {
            "reservation_id": reservation.id,
            "parking_id": parking.id,
            "parking_name": parking.parking_name,
            "cancel_time": reservation.created_at
        }
    })


@reservation_bp.route("/api/reservations", methods=["GET"])
@swag_from("../docs/reservation_list.yml")
def list_reservations():
    user_id = request.args.get("user_id")
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)

    query = Reservation.query.filter_by(user_id=user_id)
    paginated = query.paginate(page=page, per_page=size, error_out=False)

    results = []
    for r in paginated.items:
        parking = Parking.query.get(r.parking_id)
        results.append({
            "reservation_id": r.id,
            "user_id": r.user_id,
            "parking_id": parking.id,
            "parking_name": parking.parking_name,
            "address": parking.address,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "status": r.status,
            "type": "parking",
            "price_per_hour": parking.price_per_hour,
            "total_price": parking.price_per_hour * 1
        })

    return jsonify({
        "status": "success",
        "message": "예약 내역을 불러왔습니다.",
        "data": {
            "total_count": paginated.total,
            "reservations": results
        }
    })

@reservation_bp.route("/api/reservations/<int:id>", methods=["GET"])
@swag_from("../docs/reservation_detail.yml")
def get_reservation(id):
    r = Reservation.query.get(id)
    if not r:
        return jsonify({"status": "fail", "message": "예약 정보를 불러올 수 없습니다."}), 404

    parking = Parking.query.get(r.parking_id)

    return jsonify({
        "status": "success",
        "message": "주차장 예약 정보를 불러왔습니다.",
        "data": {
            "reservation_id": r.id,
            "user_id": r.user_id,
            "parking_id": parking.id,
            "parking_name": parking.parking_name,
            "address": parking.address,
            "start_time": r.start_time,
            "end_time": r.end_time,
            "status": r.status,
            "price_per_hour": parking.price_per_hour,
            "total_price": parking.price_per_hour * 1,
            "buttons": {
                "cancel": r.status == "reserved",
                "route": True
            }
        }
    })

