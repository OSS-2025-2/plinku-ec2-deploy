from flask import Blueprint, request, jsonify
from config import get_db

parking_bp = Blueprint("parking", __name__)


# GET /api/parkings
@parking_bp.route("/parkings", methods=["GET"])
def get_parkings():
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")

    conn = get_db()
    cur = conn.cursor()

    sql = "SELECT * FROM parking"

    # 정렬 옵션 처리
    if sort in ["congestion", "ev_charge"]:
        sql += f" ORDER BY {sort} {order.upper()}"

    rows = cur.execute(sql).fetchall()

    data = [dict(row) for row in rows]
    return jsonify({"status": "success", "data": data})


# GET /api/parkings/<id>
@parking_bp.route("/parkings/<int:parking_id>", methods=["GET"])
def get_parking_detail(parking_id):
    conn = get_db()
    cur = conn.cursor()

    row = cur.execute("SELECT * FROM parking WHERE id = ?", (parking_id,)).fetchone()
    if not row:
        return jsonify({"status": "fail", "message": "Not Found"}), 404

    return jsonify({"status": "success", "data": dict(row)})


# POST /api/reservations
@parking_bp.route("/reservations", methods=["POST"])
def create_reservation():
    data = request.json
    user_id = data.get("user_id")
    parking_id = data.get("parking_id")
    start_time = data.get("start_time")
    end_time = data.get("end_time")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO reservations (user_id, parking_id, start_time, end_time)
        VALUES (?, ?, ?, ?)
    """, (user_id, parking_id, start_time, end_time))

    conn.commit()
    return jsonify({"status": "success", "message": "예약 성공"})


# DELETE /api/reservations/<id>
@parking_bp.route("/reservations/<int:reservation_id>", methods=["DELETE"])
def delete_reservation(reservation_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM reservations WHERE id = ?", (reservation_id,))
    conn.commit()

    return jsonify({"status": "success", "message": "예약 취소 완료"})
