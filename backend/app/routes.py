from flask import Blueprint, jsonify,request
from .sample_data import PARKINGS, RESERVATIONS
main = Blueprint('main', __name__)



#주차장 탐색
@main.route('/api/parkings', methods=['GET'])
def list_parkings():
    page = request.args.get("page", default=1, type=int)
    size = request.args.get("size", default=10, type=int)
    sort = request.args.get("sort", default="distance_km")  # 정렬 기준
    order = request.args.get("order", default="asc")         # asc / desc
    congestion_filter = request.args.get("congestion")      # low, medium, high
    ev_filter = request.args.get("ev_charger")              # true/false
    keyword = request.args.get("keyword", default="").lower()

    #주차장 탐색 필터링
    """수업 중 배운 지능형 리스트를 사용하여 results를 생성"""
    results = [
        p for p in PARKINGS.values()
        if (not congestion_filter or p.get("congestion") == congestion_filter)
        and (not ev_filter or str(p.get("ev_charger", False)).lower() == ev_filter.lower())
        and (keyword in p.get("parking_name", "").lower() or keyword in p.get("address", "").lower())
    ]

    #정렬
    reverse = (order == "desc")

    """수업 내용 중 익명함수를 사용하여 results를 정렬"""
    results.sort(key=lambda x: x.get(sort, 0), reverse=reverse)
    #원래 문단
    #def sort_key(item):
    #       return item.get(sort, 0)
    #results.sort(key=sort_key, reverse=reverse)

    #페이지네이션
    total_count = len(results)
    start = (page - 1) * size
    end = start + size
    paginated_results = results[start:end]

    # 주차장 or 충전소 판별
    if ev_filter is not None:
        ev_filter_bool = ev_filter.lower() == "true"
        result_type = "charger" if ev_filter_bool else "parking"
    else:
        result_type = "parking"

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


#주차장 정보 조회 
@main.route('/api/parkings/<int:id>', methods=['GET'])
def get_parking(id):
    parking = PARKINGS.get(id)

    if not parking:
        return jsonify({
            "status": "fail",
            "message": "주차장 정보를 불러올 수 없습니다.",
            "error_code": "NOT_FOUND"
        }), 404

    return jsonify({
        "status": "success",
        "message": "주차장 정보를 불러왔습니다.",
        "data": parking
    }),200



#임시 예약저장소
RESERVATIONS = []

#주차장 예약 생성
@main.route('/api/reservations', methods=['POST'])
def reserve_parking():
    data = request.get_json()
    user_id = data.get("user_id")
    parking_id = data.get("parking_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")


    # 주차장이 존재하는지
    parking = PARKINGS.get(parking_id)
    if not parking:
        return jsonify({
            "status": "fail",
            "message": "존재하지 않는 주차장입니다.",
            "error_code": "NOT_FOUND"
        }), 404

    # 예약 추가 (실제 DB 대신 리스트) -> DB 구현되면 바꾸면 됩니다.
    RESERVATIONS.append({
        "user_id": user_id,
        "parking_id": parking_id,
        "start_time": start_time,
        "end_time": end_time
    })

    return jsonify({
        "status": "success",
        "message": "주차장 예약이 완료되었습니다."
    }), 200