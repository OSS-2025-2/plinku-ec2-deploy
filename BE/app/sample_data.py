# DB 연결 전 임시 데이터용
PARKINGS = {
    1: {
        "parking_id": 1,
        "parking_name": "국립한밭대학교",
        "address": "대전광역시 유성구 대학로 125",
        "price_per_hour": 1500,
        "total_spots": 10,
        "available_spots": 3,
        "distance_km": 0.5,
        "layout": [
            {"spot_id": 1, "status": "occupied", "color": "red"},
            {"spot_id": 2, "status": "available", "color": "green"},
        ],
        "buttons": {"reserve": True, "route": True},
        "ev_charger": False,
        "congestion": "low", # low / medium / high
        "type" : "parking" # parking or charger
    }
    ,
    2: {
        "parking_id": 3,
        "parking_name": "서구 공영주차장",
        "address": "대전광역시 서구 공원로 45",
        "price_per_hour": 1200,
        "total_spots": 20,
        "available_spots": 0,
        "distance_km": 2.0,
        "layout": [],
        "buttons": {"reserve": True, "route": True},
        "ev_charger": False,
        "congestion": "high",
        "type" : "parking" 
    }
}


