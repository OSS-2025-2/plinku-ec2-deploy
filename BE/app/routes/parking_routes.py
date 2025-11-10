from flask import Blueprint, jsonify, request
from app.data.sample_data import PARKINGS

parking_bp = Blueprint("parking", __name__)   

# 주차장 탐색
@parking_bp.route("/api/parkings", methods=["GET"])
def list_parkings():
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    sort = request.args.get("sort", default="distance_km")
    order = request.args.get("order", default="asc")
    congestion_filter = request.args.get("congestion")
    ev_filter = request.args.get("ev_charger", "false")
    keyword = request.args.get("keyword", default="").lower()

    results = [
        p for p in PARKINGS.values()
        if (not congestion_filter or p.get("congestion") == congestion_filter)
        and (str(p.get("ev_charger", False)).lower() == ev_filter.lower())
        and (keyword in p.get("parking_name", "").lower() or keyword in p.get("address", "").lower())
    ]

    reverse = (order == "desc")
    results.sort(key=lambda x: x.get(sort, 0), reverse=reverse)

    total_count = len(results)
    start = (page - 1) * size
    end = start + size
    paginated_results = results[start:end]

    result_type = "charger" if ev_filter.lower() == "true" else "parking"

    return jsonify({
        "status": "success",
        "message": f"{result_type} 정보를 불러왔습니다.",
        "data": {
            "type": result_type,
            "total_count": total_count,
            "page": page,
            "size": size,
            "results": paginated_results
        }
    }), 200


# 주차장 상세 조회
@parking_bp.route("/api/parkings/<int:id>", methods=["GET"])
def get_parking(id):
    parking = PARKINGS.get(id)

    if not parking:
        return jsonify({
            "status": "fail",
            "message": "주차장 또는 충전소 정보를 불러올 수 없습니다.",
            "error_code": "NOT_FOUND"
        }), 404

    return jsonify({
        "status": "success",
        "message": f"{'충전소' if parking['type'] == 'charger' else '주차장'} 정보를 불러왔습니다.",
        "data": parking
    }), 200