# app/routes/favorites_routes.py
from flask import Blueprint, jsonify, request

favorites_bp = Blueprint('favorites', __name__)


# -----------------------------
# 1) 즐겨찾기 목록 조회 (GET /api/favorites)
# -----------------------------
@favorites_bp.route('/api/favorites', methods=['GET'])
def get_favorites():
    """
    즐겨찾는 주차장/충전소 조회
    ---
    tags:
      - Favorites
    parameters:
      - name: user_id
        in: query
        type: integer
        required: true
        description: 사용자 ID
    responses:
      200:
        description: 즐겨찾기 목록 조회 성공
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: 즐겨찾는 장소 목록을 불러왔습니다.
            data:
              type: object
              properties:
                total_count:
                  type: integer
                  example: 2
                favorites:
                  type: array
                  items:
                    type: object
                    properties:
                      favorite_id:
                        type: integer
                        example: 10
                      parking_id:
                        type: integer
                        example: 5
                      parking_name:
                        type: string
                        example: A주차장
                      address:
                        type: string
                        example: 서울시 강남구 테헤란로 123
                      distance_km:
                        type: number
                        example: 1.2
                      ev_charger:
                        type: boolean
                        example: false
                      type:
                        type: string
                        example: parking
                      price_per_hour:
                        type: integer
                        example: 1500
                      buttons:
                        type: object
                        properties:
                          detail:
                            type: boolean
                            example: true
                          route:
                            type: boolean
                            example: true
                          delete:
                            type: boolean
                            example: true
      400:
        description: 실패 시
        schema:
          type: object
          properties:
            status:
              type: string
              example: fail
            message:
              type: string
              example: 즐겨찾는 목록을 불러올 수 없습니다.
    """
    pass



# -----------------------------
# 2) 즐겨찾기 등록 (POST /api/parkings/{id}/favorite)
# -----------------------------
@favorites_bp.route('/api/parkings/<int:parking_id>/favorite', methods=['POST'])
def add_favorite(parking_id):
    """
    즐겨찾기 등록
    ---
    tags:
      - Favorites
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: 즐겨찾기 등록 성공
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: 주차장이 즐겨찾기에 추가되었습니다.
            data:
              type: object
              properties:
                type:
                  type: string
                  example: parking
                favorite_id:
                  type: integer
                  example: 7
                parking_id:
                  type: integer
                  example: 5
                parking_name:
                  type: string
                  example: A주차장
                address:
                  type: string
                  example: 서울시 강남구
                price_per_hour:
                  type: integer
                  example: 1500
                distance_km:
                  type: number
                  example: 1.2
                ev_charger:
                  type: boolean
                  example: false
                buttons:
                  type: object
                  properties:
                    delete:
                      type: boolean
                      example: true
                    route:
                      type: boolean
                      example: true
      400:
        description: 실패 시
        schema:
          type: object
          properties:
            status:
              type: string
              example: fail
            message:
              type: string
              example: 즐겨찾기 등록에 실패했습니다.
    """
    pass



# -----------------------------
# 3) 즐겨찾기 해제 (DELETE /api/parkings/{id}/favorite)
# -----------------------------
@favorites_bp.route('/api/parkings/<int:parking_id>/favorite', methods=['DELETE'])
def remove_favorite(parking_id):
    """
    즐겨찾기 해제
    ---
    tags:
      - Favorites
    parameters:
      - name: parking_id
        in: path
        type: integer
        required: true
      - name: user_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: 즐겨찾기 해제 성공
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: 즐겨찾기가 해제되었습니다.
            data:
              type: object
              properties:
                type:
                  type: string
                  example: parking
                favorite_id:
                  type: integer
                  example: 7
                parking_id:
                  type: integer
                  example: 5
                parking_name:
                  type: string
                  example: A주차장
                address:
                  type: string
                  example: 서울시 강남구
                ev_charger:
                  type: boolean
                  example: false
                buttons:
                  type: object
                  properties:
                    add:
                      type: boolean
                      example: true
                    route:
                      type: boolean
                      example: true
      400:
        description: 실패 시
        schema:
          type: object
          properties:
            status:
              type: string
              example: fail
            message:
              type: string
              example: 즐겨찾기를 해제할 수 없습니다.
    """
    pass



# -----------------------------
# 4) 즐겨찾기 전체 삭제 (DELETE /api/favorites)
# -----------------------------
@favorites_bp.route('/api/favorites', methods=['DELETE'])
def delete_all_favorites():
    """
    즐겨찾기 전체 삭제
    ---
    tags:
      - Favorites
    parameters:
      - name: user_id
        in: query
        type: integer
        required: true
    responses:
      200:
        description: 즐겨찾기 전체 삭제 성공
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: 즐겨찾기 목록이 모두 삭제되었습니다.
            data:
              type: object
              properties:
                deleted_count:
                  type: integer
                  example: 12
    """
    pass
