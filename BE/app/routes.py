from flask import Blueprint, jsonify,request
from .sample_data import PARKINGS
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

    # 버튼 클릭에 따라 기본값 전달 가능
    # 기본: 주차장 리스트
    ev_filter = request.args.get("ev_charger")
    if ev_filter is None:
        ev_filter = "false"


    #주차장 탐색 필터링
    """수업 중 배운 지능형 리스트를 사용하여 results를 생성"""
    results = [
        p for p in PARKINGS.values()
        if (not congestion_filter or p.get("congestion") == congestion_filter)
        and (str(p.get("ev_charger", False)).lower() == ev_filter.lower())
        and (keyword in p.get("parking_name", "").lower() or keyword in p.get("address", "").lower())
    ]
    #원래문단
    #results = []
    #for p in PARKINGS.values():
    # if congestion_filter and p.get("congestion") != congestion_filter:
        #continue
    # if ev_filter and str(p.get("ev_charger", False)).lower() != ev_filter.lower():
        #continue
    # if not (keyword in p.get("parking_name", "").lower() or
            # keyword in p.get("address", "").lower()):
        #continue
    #results.append(p)

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




@main.route('/api/parkings/<int:id>', methods=['GET'])
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
