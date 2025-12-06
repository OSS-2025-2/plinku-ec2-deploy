# PLINKU_PROJECT/BE/app/routes/parking_routes.py
import os
from flask import current_app
from flask import Blueprint, request, jsonify
from app.models.parking import Parking, ParkingSpot
from app.config import db
from flasgger import swag_from

parking_bp = Blueprint("parking", __name__)


@parking_bp.route("/api/parkings", methods=["GET"])
@swag_from("../docs/parking_list.yml")
def list_parkings():
    page = request.args.get("page", 1, type=int)
    size = request.args.get("size", 10, type=int)
    sort = request.args.get("sort", "distance_km")
    order = request.args.get("order", "asc")

    keyword = request.args.get("keyword", "").lower()
    ev_filter = request.args.get("ev_charger")
    congestion_filter = request.args.get("congestion")
    type_filter = request.args.get("type")

    query = Parking.query

    # 검색 필터
    if keyword:
        query = query.filter(
            Parking.parking_name.ilike(f"%{keyword}%") |
            Parking.address.ilike(f"%{keyword}%")
        )

    # 🔥 EV 필터: spot 기반
    if ev_filter:
        want_ev = ev_filter.lower() == "true"
        if want_ev:
            query = query.filter(Parking.spots.any(ParkingSpot.ev_charge == True))
        else:
            query = query.filter(~Parking.spots.any(ParkingSpot.ev_charge == True))

    # 혼잡도 필터
    if congestion_filter:
        query = query.filter(Parking.congestion == congestion_filter)

    # 타입 필터
    if type_filter == "ev":
        query = query.filter(Parking.spots.any(ParkingSpot.ev_charge == True))
    elif type_filter == "parking":
        query = query.filter(~Parking.spots.any(ParkingSpot.ev_charge == True))

    # 정렬
    # ---------------------
    # 정렬 기준 설정 (sort와 order 파라미터 활용)
    sort_column = getattr(Parking, sort, None)
    if not sort_column:
        return jsonify({"error": f"Invalid sort column: {sort}"}), 400

    if order == "desc":
        query = query.order_by(sort_column.desc()) # 내림차순 정렬
    else:
        query = query.order_by(sort_column.asc())# 오름차순 정렬

    paginated = query.paginate(page=page, per_page=size, error_out=False)

    results = []
    for p in paginated.items:

        # 🔥 available, EV 존재 여부 spot 기반 계산
        available_count = sum(1 for s in p.spots if s.status == "available")
        ev_exists = any(s.ev_charge for s in p.spots)

        results.append({
            "id": p.id,
            "parking_name": p.parking_name,
            "address": p.address,
            "price_per_hour": p.price_per_hour,
            "available_spots": available_count,
            "distance_km": p.distance_km,
            "ev_charge": ev_exists,
            "congestion": p.congestion,
            "type": p.type
        })

    return jsonify({
        "status": "success",
        "page": page,
        "size": size,
        "total": paginated.total,
        "pages": paginated.pages,
        "results": results
    })

# -----------------------
# 주차장 상세 정보 조회 API
# -----------------------

@parking_bp.route("/api/parkings/<int:id>", methods=["GET"])
@swag_from("../docs/parking_detail.yml")
def get_parking(id):
    p = Parking.query.get(id)
    if not p:
        return jsonify({"status": "fail", "message": "NOT FOUND"}), 404

    spots = []
    for s in p.spots:
        spots.append({
            "id": s.id,               # 🔥 반드시 넣어야 함 (중복되지 않는 PK)
            "spot_id": s.spot_id,     # UI 표기용 번호
            "status": s.status,
            "color": s.color,
            "ev_charge": s.ev_charge
        })

    available_count = sum(1 for s in p.spots if s.status == "available")
    occupied_count = sum(1 for s in p.spots if s.status == "occupied")

    return jsonify({
        "status": "success",
        "data": {
            "parking_id": p.id,
            "parking_name": p.parking_name,
            "address": p.address,
            "price_per_hour": p.price_per_hour,
            "total_spots": p.total_spots,
            "available_spots": available_count,
            "occupied_spots": occupied_count,
            "distance_km": p.distance_km,
            "lat": p.lat,
            "lng": p.lng,
            "layout": spots,
            "buttons": {
                "reserve": True,
                "route": True
            }
        }
    })

