#PLINKU_PROJECT/BE/app/routes/parking_routes.py
import os
from flask import current_app
from flask import Blueprint, request, jsonify
from app.models.parking import Parking, ParkingSpot, ParkingButton
from app.config import db
from flasgger import swag_from


parking_bp = Blueprint("parking", __name__)

  # <=== YAML 문서 연결
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

    # ---------------------
    # 기본 쿼리 구성
    # ---------------------
    query = Parking.query
# 검색 기능 (주차장 이름 또는 주소로 검색)
    if keyword:
        query = query.filter(
            Parking.parking_name.ilike(f"%{keyword}%") |
            Parking.address.ilike(f"%{keyword}%")
        )

    if ev_filter:
        query = query.filter(Parking.ev_charge == (ev_filter.lower() == "true"))

    if congestion_filter:
        query = query.filter(Parking.congestion == congestion_filter)

    # ---------------------
    # 정렬
    # ---------------------
    # 정렬 기준 설정 (sort와 order 파라미터 활용)
    sort_column = getattr(Parking, sort, None)
    if sort_column is None:
        return jsonify({"error": f"Invalid sort column: {sort}"}), 400

    if order == "desc":
        query = query.order_by(sort_column.desc()) # 내림차순 정렬
    else:
        query = query.order_by(sort_column.asc())# 오름차순 정렬

    # ---------------------
    # 페이지네이션
    # ---------------------
    paginated = query.paginate(page=page, per_page=size, error_out=False)

    results = []
    for p in paginated.items:
        results.append({
            "id": p.id,
            "parking_name": p.parking_name,
            "address": p.address,
            "price_per_hour": p.price_per_hour,
            "available_spots": p.available_spots,
            "distance_km": p.distance_km,
            "ev_charge": p.ev_charge,
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
            "spot_id": s.spot_id,
            "status": s.status,
            "color": s.color
        })

    return jsonify({
        "status": "success",
        "data": {
            "parking_id": p.id,
            "parking_name": p.parking_name,
            "address": p.address,
            "price_per_hour": p.price_per_hour,
            "total_spots": p.total_spots,
            "available_spots": p.available_spots,
            "distance_km": p.distance_km,
            "layout": spots,
            "buttons": {
                "reserve": True,
                "route": True
            }
        }
    })
