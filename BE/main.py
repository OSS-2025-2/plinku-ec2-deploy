"""
PlinkU 주차장 예약 시스템 백엔드
Flask 기반 REST API 서버
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from functools import wraps
import json

app = Flask(__name__)
CORS(app)  # 프론트엔드와 통신을 위한 CORS 설정

# ============================================================================
# 자료구조 활용: Dictionary, Set 기반 인메모리 데이터 저장소
# ============================================================================
# 
# [Dictionary 기반 빠른 조회(O(1))]
# 해시 기반 조회(O(1)) — ParkingSpot, User 등 빠른 조회 구조 설계에 유리.
# dict comprehension — JSON 변환 시 빠르고 간결하게 response 구성 가능.
# 딕셔너리(dict): key → value 매핑 → 주차장 한 개의 상세 정보(이름, 가격, 좌표 등)를 한 번에 표현.
# 가변 객체(mutable object): 딕셔너리처럼 내부 상태 변경 가능 → 함수 기본값으로 쓰면 안 되는 타입.

# Dictionary 기반 조회(O(1)) - ParkingSpot, User 등 빠른 조회 구조
parking_spots: Dict[int, Dict] = {}  # {id: spot_data} - 해시 기반 O(1) 조회
ev_stations: Dict[int, Dict] = {}  # {id: station_data} - 해시 기반 O(1) 조회
users: Dict[int, Dict] = {}  # {id: user_data} - 해시 기반 O(1) 조회
reservations: Dict[int, Dict] = {}  # {id: reservation_data} - 해시 기반 O(1) 조회
posts: Dict[int, Dict] = {}  # {id: post_data} - 해시 기반 O(1) 조회
comments: Dict[int, Dict] = {}  # {id: comment_data} - 해시 기반 O(1) 조회

# [Set 기반 중복 체크 및 집합 연산]
# 중복 제거(set) — 주차장 타입, EV 여부 필터 등에서 중복 없는 집합 처리 시 유용.
# 집합(set): 중복 없는 값의 모음 → 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용.
# set operations(교집합/합집합/차집합) — 필터 기능(예: EV+빈자리+근처거리)에 응용 가능.

# Set 기반 중복 제거 및 빠른 조회
favorites: Dict[int, Set[int]] = {}  # {user_id: {spot_id1, spot_id2, ...}} - Set으로 중복 자동 제거
blocked_users: Set[int] = set()  # 차단된 유저 ID 집합 - Set operations로 빠른 조회
reserved_slots: Dict[str, Set[int]] = {}  # {"place_type:place_id": {slot1, slot2, ...}} - place_type과 place_id를 조합한 키로 충돌 방지, Set으로 중복 체크
post_likes: Dict[int, Set[int]] = {}  # {post_id: {user_id1, user_id2, ...}} - 좋아요 기능, Set으로 중복 체크

# ID 카운터 (자동 증가)
id_counters = {
    'parking_spot': 0,
    'ev_station': 0,
    'user': 0,
    'reservation': 0,
    'post': 0,
    'comment': 0
}

# 사용자 인증은 헤더의 X-User-Id로 처리

# ============================================================================
# 시퀀스 기반 구조: 커스텀 리스트 클래스 (__getitem__, 슬라이싱, __contains__)
# ============================================================================
# 
# [Sequence 기반 구조 (리스트 동작 최적화)]
# __getitem__으로 반복 가능 객체 만들기 — DB 모델 결과를 커스텀 리스트처럼 만들 수 있음.
# 슬라이싱 지원 — Pagination 내부 구조를 커스텀 시퀀스로 구현 가능.
# __contains__ 오버라이드 — 특정 ID 포함 여부 같은 로직 최적화 가능.
# 
# [파이썬 기본 자료형 / 시퀀스 계열]
# 리스트(list): 순서 있는 가변 컬렉션 → 주차장 목록, 댓글 목록, 즐겨찾기 리스트 저장.
# 슬라이싱(slicing): list[a:b] 잘라 쓰기 → 페이징, 일부 구간만 보여줄 때 재활용.
# 리스트 컴프리헨션(list comprehension): 한 줄로 리스트 생성 → 더미데이터, id 목록, 필터링 결과 만드는 데 사용.

class ParkingSpotList:
    """
    Sequence 기반 구조: __getitem__으로 반복 가능 객체 만들기
    슬라이싱 지원: Pagination 내부 구조를 커스텀 시퀀스로 구현
    __contains__ 오버라이드: 특정 ID 포함 여부 같은 로직 최적화
    
    선형 리스트(배열형 리스트): 인덱스로 바로 접근 가능한 연속 메모리 리스트 → 이미 파이썬 list가 이 역할
    """
    def __init__(self, spots: Dict[int, Dict]):
        self._spots = spots
        self._sorted_ids = sorted(spots.keys())
    
    def __getitem__(self, key):
        """
        인덱스로 바로 접근 가능한 연속 메모리 리스트처럼 동작
        선형 리스트(배열형 리스트): 인덱스로 바로 접근 가능한 연속 메모리 리스트
        """
        if isinstance(key, slice):
            # 슬라이싱 지원: 페이징 결과에서 특정 구간만 반환
            # 슬라이싱(slicing): list[a:b] 잘라 쓰기 → 페이징, 일부 구간만 보여줄 때 재활용
            # 슬라이스에 할당 / del: 슬라이싱을 이용해 중간 구간 삭제/치환 → 페이징 결과에서 특정 구간 제거, 다수 레코드 한번에 교체에 응용
            ids = self._sorted_ids[key]
            # 리스트 컴프리헨션: 한 줄로 리스트 생성 → 필터링 결과 만드는 데 사용
            return [self._spots[id] for id in ids]
        return self._spots[self._sorted_ids[key]]
    
    def __len__(self):
        return len(self._spots)
    
    def __contains__(self, item):
        """
        특정 ID 포함 여부 같은 로직 최적화
        __contains__ 오버라이드 — 특정 ID 포함 여부 같은 로직 최적화 가능
        """
        return item in self._spots
    
    def __iter__(self):
        """
        반복 가능 객체
        일급 객체(first-class function): 함수를 변수처럼 저장, 인자로 넘기고, 반환값으로 돌려줄 수 있음
        """
        for id in self._sorted_ids:
            yield self._spots[id]
    
    def filter(self, **kwargs):
        """
        필터링 기능
        리스트 컴프리헨션: 한 줄로 리스트 생성 → 필터링 결과 만드는 데 사용
        """
        result = []
        for spot in self:
            match = True
            for key, value in kwargs.items():
                if spot.get(key) != value:
                    match = False
                    break
            if match:
                result.append(spot)
        return result


# ============================================================================
# 퍼스트 클래스 함수 / 함수형 요소
# ============================================================================
# 
# [퍼스트 클래스 함수 / 함수형 요소]
# 일급 객체(first-class function): 함수를 변수처럼 저장, 인자로 넘기고, 반환값으로 돌려줄 수 있음 → 전략 함수, 콜백, 훅 구현에 핵심.
# 고차 함수(higher-order function): 함수를 받거나 반환하는 함수 → 공통 로직 래핑, 미들웨어 느낌으로 사용.
# 익명 함수(lambda): 한 줄짜리 작은 함수 → 정렬 기준, 간단 필터 조건에 사용.
# callable 객체: __call__ 가진 클래스 인스턴스 → "함수처럼 행동하는 객체" 만들어서 상태+로직 묶을 때 사용.
# map / filter / reduce 대체: 리스트 컴프리헨션 + generator로 깔끔하게 데이터 변환/필터링 → 조회 결과 처리, 통계 계산 등에서 응용.

def get_next_id(entity_type: str) -> int:
    """
    ID 생성 함수
    일급 객체(first-class function): 함수를 변수처럼 저장, 인자로 넘기고, 반환값으로 돌려줄 수 있음
    """
    id_counters[entity_type] += 1
    return id_counters[entity_type]


# 고차 함수: 함수를 받거나 반환하는 함수
def validate_required_fields(*required_fields):
    """
    고차 함수: 공통 로직 래핑, 미들웨어 느낌으로 사용
    데코레이터 패턴으로 요청 데이터 검증
    
    고차 함수(higher-order function): 함수를 받거나 반환하는 함수 → 공통 로직 래핑, 미들웨어 느낌으로 사용.
    클로저(closure): 함수 안에서 외부 변수 캡처해서 상태를 기억하는 함수 → 간단한 캐시, 카운터, 설정이 들어간 함수 만들 때 사용.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            data = request.get_json() or {}
            # 리스트 컴프리헨션: 한 줄로 리스트 생성 → 필터링 결과 만드는 데 사용
            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing)}'
                }), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# 데코레이터 / 클로저
# ============================================================================
# 
# [데코레이터 / 클로저]
# 클로저(closure): 함수 안에서 외부 변수 캡처해서 상태를 기억하는 함수 → 간단한 캐시, 카운터, 설정이 들어간 함수 만들 때 사용.
# nonlocal: 클로저 내부에서 바깥 스코프 변수 수정할 때 쓰는 키워드.
# 함수 데코레이터(function decorator): 다른 함수를 감싸서 기능을 추가하는 함수 → 인증 체크, 로깅, 실행 시간 측정, 트랜잭션 처리 같은 공통 기능에 바로 적용 가능.
# 등록용 데코레이터(registration decorator): 어떤 함수들을 자동으로 레지스트리에 모아두는 패턴 → "이벤트 핸들러 목록", "프로모션 전략 목록"처럼 플러그인 모으는 데 사용.

def require_auth(func):
    """
    함수 데코레이터: 인증 체크, 로깅, 실행 시간 측정 같은 공통 기능에 바로 적용
    클로저: 외부 변수 캡처해서 상태를 기억하는 함수
    
    함수 데코레이터(function decorator): 다른 함수를 감싸서 기능을 추가하는 함수 → 인증 체크, 로깅, 실행 시간 측정, 트랜잭션 처리 같은 공통 기능에 바로 적용 가능.
    클로저(closure): 함수 안에서 외부 변수 캡처해서 상태를 기억하는 함수 → 간단한 캐시, 카운터, 설정이 들어간 함수 만들 때 사용.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_id = request.headers.get('X-User-Id', type=int)
        # Dictionary 기반 조회(O(1)) - User 빠른 조회 구조
        if user_id is None or user_id not in users:
            return jsonify({'error': 'Authentication required'}), 401
        # request에 user_id 추가
        request.user_id = user_id
        return func(*args, **kwargs)
    return wrapper


# 등록용 데코레이터: 이벤트 핸들러 목록처럼 플러그인 모으는 데 사용
event_handlers = {}  # 딕셔너리: key → value 매핑 → 이벤트 타입별 핸들러 목록 저장

def register_handler(event_type: str):
    """
    등록용 데코레이터: 프로모션 전략 목록처럼 플러그인 모으는 데 사용
    
    등록용 데코레이터(registration decorator): 어떤 함수들을 자동으로 레지스트리에 모아두는 패턴 → "이벤트 핸들러 목록", "프로모션 전략 목록"처럼 플러그인 모으는 데 사용.
    클로저(closure): 함수 안에서 외부 변수 캡처해서 상태를 기억하는 함수
    """
    def decorator(func):
        if event_type not in event_handlers:
            event_handlers[event_type] = []  # 리스트: 순서 있는 가변 컬렉션 → 핸들러 목록 저장
        event_handlers[event_type].append(func)
        return func
    return decorator


# ============================================================================
# 스택 / 큐 구조
# ============================================================================
# 
# [스택 / 큐]
# 스택(Stack): LIFO 구조 → 이전 페이지/이전 검색 조건 되돌리기(undo), 깊이우선 탐색 같은 데 사용.
# 함수 호출 스택 개념: 재귀, 예외 처리, 콜 스택 이해에 필요 → 복잡한 재귀 알고리즘 디버깅할 때 머릿속 모델.
# 큐(Queue): FIFO 구조 → 예약 처리 대기열, 알림 발송 대기열, 비동기 작업 큐 개념을 이해하는 데 사용.
# 우선순위 큐(Priority Queue): 우선순위 높은 작업 먼저 처리 → 예) 혼잡도 높은 주차장/긴급 요청 먼저 처리하는 로직에 응용 가능.

# 스택: LIFO 구조 - 이전 페이지/이전 검색 조건 되돌리기(undo)
# 리스트(list): 순서 있는 가변 컬렉션 → 네비게이션 히스토리 저장
navigation_stack: List[Dict] = []

def push_navigation(route: str, data: Dict = None):
    """
    스택: 이전 페이지 되돌리기(undo)
    스택(Stack): LIFO 구조 → 이전 페이지/이전 검색 조건 되돌리기(undo), 깊이우선 탐색 같은 데 사용.
    """
    navigation_stack.append({'route': route, 'data': data, 'timestamp': datetime.now()})

def pop_navigation() -> Optional[Dict]:
    """
    스택: 이전 페이지 되돌리기(undo)
    스택(Stack): LIFO 구조 → 이전 페이지/이전 검색 조건 되돌리기(undo)
    """
    return navigation_stack.pop() if navigation_stack else None


# 우선순위 큐: 우선순위 높은 작업 먼저 처리
# (혼잡도 높은 주차장/긴급 요청 먼저 처리하는 로직에 응용 가능)
from heapq import heappush, heappop

# 리스트(list): 순서 있는 가변 컬렉션 → 우선순위 큐 저장
priority_queue = []

def add_priority_task(priority: int, task: Dict):
    """
    우선순위 큐: 혼잡도 높은 주차장/긴급 요청 먼저 처리
    
    우선순위 큐(Priority Queue): 우선순위 높은 작업 먼저 처리 → 예) 혼잡도 높은 주차장/긴급 요청 먼저 처리하는 로직에 응용 가능.
    튜플(tuple): 순서 있지만 불변 → (우선순위, 타임스탬프, 작업) 같은 변경되면 안 되는 묶음에 사용.
    """
    # 튜플(tuple): 순서 있지만 불변 → (우선순위, 타임스탬프, 작업) 같은 변경되면 안 되는 묶음에 사용
    heappush(priority_queue, (priority, datetime.now(), task))

def get_next_priority_task() -> Optional[Dict]:
    """
    우선순위 큐: 우선순위 높은 작업 먼저 처리
    
    우선순위 큐(Priority Queue): 우선순위 높은 작업 먼저 처리 → 예) 혼잡도 높은 주차장/긴급 요청 먼저 처리하는 로직에 응용 가능.
    """
    if priority_queue:
        _, _, task = heappop(priority_queue)
        return task
    return None


# 더미 데이터 제거 - 호스팅 바로 할 수 있게 빈 상태로 시작


# ============================================================================
# API 엔드포인트
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'ok', 'message': 'PlinkU API is running'})


# ============================================================================
# 인증 API
# ============================================================================

@app.route('/api/signup', methods=['POST'])
@validate_required_fields('email', 'password')
def signup():
    """
    회원가입
    Dictionary 기반 조회(O(1)) - User 빠른 조회 구조
    """
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    # Set operations: 중복 체크 (이미 등록된 이메일인지 확인)
    existing_user = next((u for u in users.values() if u['email'] == email), None)
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400
    
    user_id = get_next_id('user')
    users[user_id] = {
        'id': user_id,
        'email': email,
        'password': password,  # 실제로는 해시화 필요
        'name': data.get('name', email.split('@')[0])
    }
    
    return jsonify({
        'message': 'Signup successful',
        'user': {'id': user_id, 'email': email}
    }), 201


@app.route('/api/login', methods=['POST'])
@validate_required_fields('email', 'password')
def login():
    """
    로그인
    Dictionary 기반 조회(O(1)) - User 빠른 조회 구조
    """
    data = request.get_json()
    email = data['email']
    password = data['password']
    
    # Dictionary 기반 조회로 사용자 찾기
    user = next((u for u in users.values() if u['email'] == email and u['password'] == password), None)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user['id'], 'email': user['email'], 'name': user['name']}
    })


@app.route('/api/logout', methods=['POST'])
def logout():
    """로그아웃"""
    return jsonify({'message': 'Logout successful'})


# ============================================================================
# 주차장 API
# ============================================================================

@app.route('/api/parking-spots', methods=['GET'])
def get_parking_spots():
    """
    주차장 목록 조회
    Dictionary 기반 조회(O(1)) - ParkingSpot 빠른 조회 구조
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    슬라이싱: 페이징, 일부 구간만 보여줄 때 재활용
    """
    # 페이징 파라미터
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Query parameters로 필터링
    is_ev = request.args.get('is_ev', type=bool)
    max_distance = request.args.get('max_distance', type=float)
    min_available = request.args.get('min_available', type=int)
    
    # 리스트 컴프리헨션으로 필터링
    # 리스트 컴프리헨션(list comprehension): 한 줄로 리스트 생성 → 더미데이터, id 목록, 필터링 결과 만드는 데 사용.
    # map / filter / reduce 대체: 리스트 컴프리헨션 + generator로 깔끔하게 데이터 변환/필터링 → 조회 결과 처리, 통계 계산 등에서 응용.
    filtered_spots = [
        spot for spot in parking_spots.values()
        if (is_ev is None or spot.get('is_ev') == is_ev)
        and (max_distance is None or spot.get('distance', 0) <= max_distance)
        and (min_available is None or spot.get('available', 0) >= min_available)
    ]
    
    # 슬라이싱: 페이징, 일부 구간만 보여줄 때 재활용
    # 슬라이싱(slicing): list[a:b] 잘라 쓰기 → 페이징, 일부 구간만 보여줄 때 재활용.
    # 슬라이스에 할당 / del: 슬라이싱을 이용해 중간 구간 삭제/치환 → 페이징 결과에서 특정 구간 제거, 다수 레코드 한번에 교체에 응용.
    start = (page - 1) * per_page
    end = start + per_page
    paginated_spots = filtered_spots[start:end]
    
    # Dictionary comprehension: JSON 변환 시 빠르고 간결하게 response 구성
    # dict comprehension — JSON 변환 시 빠르고 간결하게 response 구성 가능.
    return jsonify({
        'spots': paginated_spots,
        'count': len(filtered_spots),
        'page': page,
        'per_page': per_page
    })


@app.route('/api/parking-spots/<int:spot_id>', methods=['GET'])
def get_parking_spot(spot_id):
    """
    주차장 상세 조회
    Dictionary 기반 조회(O(1)) - ParkingSpot 빠른 조회 구조
    """
    spot = parking_spots.get(spot_id)
    if not spot:
        return jsonify({'error': 'Parking spot not found'}), 404
    
    # 2차원 리스트: 주차구역 그리드, 좌석/구획 배치 같은 표 형태 데이터
    # 2차원 리스트: 리스트 안에 리스트 → 주차구역 그리드, 좌석/구획 배치 같은 표 형태 데이터.
    slots = []  # 리스트(list): 순서 있는 가변 컬렉션 → 주차장 슬롯 목록 저장
    total_slots = spot.get('total', 12)
    rows = spot.get('rows', 3)
    cols = spot.get('cols', 4)
    # place_type과 place_id를 조합한 키로 충돌 방지
    # Dictionary 기반 조회(O(1)) - reserved_slots 빠른 조회 구조
    reserved_key = f"parking:{spot_id}"
    # Set 기반 중복 제거 - 이미 예약된 슬롯인지 확인
    reserved = reserved_slots.get(reserved_key, set())
    
    for i in range(total_slots):
        row = i // cols
        col = i % cols
        slots.append({
            'id': i,
            'row': row,
            'col': col,
            'taken': i in reserved,
            'free': i not in reserved
        })
    
    spot_detail = spot.copy()
    spot_detail['slots'] = slots
    spot_detail['rows'] = rows
    spot_detail['cols'] = cols
    
    return jsonify(spot_detail)


@app.route('/api/parking-spots', methods=['POST'])
@require_auth
@validate_required_fields('name', 'address')
def create_parking_spot():
    """
    주차장 등록
    Dictionary 기반 조회(O(1)) - ParkingSpot 빠른 조회 구조
    """
    data = request.get_json()
    spot_id = get_next_id('parking_spot')
    
    # 행렬 정보 (rows, cols) 추가
    rows = data.get('rows', 3)
    cols = data.get('cols', 4)
    total = data.get('total', rows * cols)
    
    new_spot = {
        'id': spot_id,
        'name': data['name'],
        'address': data['address'],
        'distance': data.get('distance', 0),
        'available': data.get('available', total),
        'total': total,
        'rows': rows,
        'cols': cols,
        'price_per_hour': data.get('price_per_hour', 1000),
        'operating_hours': data.get('operating_hours', '24시간'),
        'image': data.get('image', ''),
        'is_ev': data.get('is_ev', False),
        # 튜플(tuple): 순서 있지만 불변 → (위도, 경도), (id, 이름) 같은 변경되면 안 되는 묶음에 사용.
        # 불변 객체(immutable object): 튜플, 문자열처럼 변경 불가 → 안전하게 키, 캐시, dict 키로 사용.
        'latitude': data.get('latitude', 0),
        'longitude': data.get('longitude', 0),
        'description': data.get('description', ''),
        'owner_id': request.user_id
    }
    
    parking_spots[spot_id] = new_spot
    return jsonify(new_spot), 201


@app.route('/api/parking-spots/<int:spot_id>', methods=['PUT'])
@require_auth
def update_parking_spot(spot_id):
    """
    주차장 수정
    Dictionary 기반 조회(O(1)) - ParkingSpot 빠른 조회 구조
    """
    spot = parking_spots.get(spot_id)
    if not spot:
        return jsonify({'error': 'Parking spot not found'}), 404
    
    # 소유자 확인
    if spot.get('owner_id') != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    # 가변 객체(mutable object): 딕셔너리 내부 상태 변경
    # 가변 객체(mutable object): 리스트, 딕셔너리처럼 내부 상태 변경 가능 → 함수 기본값으로 쓰면 안 되는 타입.
    # dict comprehension — JSON 변환 시 빠르고 간결하게 response 구성 가능.
    spot.update({k: v for k, v in data.items() if k != 'id'})
    
    return jsonify(spot)


@app.route('/api/parking-spots/<int:spot_id>', methods=['DELETE'])
@require_auth
def delete_parking_spot(spot_id):
    """
    주차장 삭제
    Dictionary 기반 조회(O(1)) - ParkingSpot 빠른 조회 구조
    """
    spot = parking_spots.get(spot_id)
    if not spot:
        return jsonify({'error': 'Parking spot not found'}), 404
    
    # 소유자 확인
    if spot.get('owner_id') != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    del parking_spots[spot_id]
    return jsonify({'message': 'Parking spot deleted'})


@app.route('/api/my-parking-spots', methods=['GET'])
@require_auth
def get_my_parking_spots():
    """
    내 주차장 목록
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    """
    # 리스트 컴프리헨션으로 내 주차장 필터링
    my_spots = [spot for spot in parking_spots.values() if spot.get('owner_id') == request.user_id]
    return jsonify({'spots': my_spots, 'count': len(my_spots)})


# ============================================================================
# 즐겨찾기 API
# ============================================================================

@app.route('/api/favorites', methods=['GET'])
@require_auth
def get_favorites():
    """
    즐겨찾기 목록
    Set 기반 중복 제거 - 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용
    Set operations(교집합/합집합/차집합) - 필터 기능에 응용
    
    집합(set): 중복 없는 값의 모음 → 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용.
    set operations(교집합/합집합/차집합) — 필터 기능(예: EV+빈자리+근처거리)에 응용 가능.
    """
    # Dictionary 기반 조회(O(1)) - favorites 빠른 조회 구조
    # Set 기반 중복 제거 - 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용
    user_favorites = favorites.get(request.user_id, set())
    # Dictionary 기반 조회로 즐겨찾기 주차장 정보 가져오기
    # 리스트 컴프리헨션: 한 줄로 리스트 생성 → 필터링 결과 만드는 데 사용
    # dict comprehension — JSON 변환 시 빠르고 간결하게 response 구성 가능.
    favorite_spots = [
        {**parking_spots[fid], 'type': 'parking'} 
        for fid in user_favorites if fid in parking_spots
    ]
    favorite_stations = [
        {**ev_stations[fid], 'type': 'ev'} 
        for fid in user_favorites if fid in ev_stations
    ]
    all_favorites = favorite_spots + favorite_stations
    return jsonify({'favorites': all_favorites, 'count': len(all_favorites)})


@app.route('/api/favorites/<int:spot_id>', methods=['POST'])
@require_auth
def add_favorite(spot_id):
    """
    즐겨찾기 추가 (주차장 또는 충전소)
    Set 기반 중복 제거 - 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용
    """
    data = request.get_json() or {}
    place_type = data.get('place_type')  # 'parking' or 'ev'
    
    # place_type에 따라 확인
    if place_type == 'parking':
        if spot_id not in parking_spots:
            return jsonify({'error': 'Parking spot not found'}), 404
    elif place_type == 'ev':
        if spot_id not in ev_stations:
            return jsonify({'error': 'EV station not found'}), 404
    else:
        # place_type이 없으면 둘 다 확인 (하위 호환성)
        if spot_id not in parking_spots and spot_id not in ev_stations:
            return jsonify({'error': 'Parking spot or EV station not found'}), 404
    
    if request.user_id not in favorites:
        favorites[request.user_id] = set()
    
    # Set operations: 중복 체크
    # 집합(set): 중복 없는 값의 모음 → 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용.
    # set operations(교집합/합집합/차집합) — 필터 기능(예: EV+빈자리+근처거리)에 응용 가능.
    favorites[request.user_id].add(spot_id)
    return jsonify({'message': 'Favorite added'})


@app.route('/api/favorites/<int:spot_id>', methods=['DELETE'])
@require_auth
def remove_favorite(spot_id):
    """
    즐겨찾기 삭제
    Set operations: 중복 제거
    """
    if request.user_id in favorites:
        favorites[request.user_id].discard(spot_id)
    return jsonify({'message': 'Favorite removed'})


# ============================================================================
# 충전소 API
# ============================================================================

@app.route('/api/ev-stations', methods=['GET'])
def get_ev_stations():
    """
    충전소 목록 조회
    Dictionary 기반 조회(O(1)) - EVStation 빠른 조회 구조
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    슬라이싱: 페이징, 일부 구간만 보여줄 때 재활용
    """
    # 페이징 파라미터
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 리스트 컴프리헨션으로 필터링
    max_distance = request.args.get('max_distance', type=float)
    min_available = request.args.get('min_available', type=int)
    
    filtered_stations = [
        station for station in ev_stations.values()
        if (max_distance is None or station.get('distance', 0) <= max_distance)
        and (min_available is None or station.get('available', 0) >= min_available)
    ]
    
    # 슬라이싱: 페이징, 일부 구간만 보여줄 때 재활용
    start = (page - 1) * per_page
    end = start + per_page
    paginated_stations = filtered_stations[start:end]
    
    return jsonify({
        'stations': paginated_stations,
        'count': len(filtered_stations),
        'page': page,
        'per_page': per_page
    })


@app.route('/api/ev-stations/<int:station_id>', methods=['GET'])
def get_ev_station(station_id):
    """
    충전소 상세 조회
    Dictionary 기반 조회(O(1)) - EVStation 빠른 조회 구조
    """
    station = ev_stations.get(station_id)
    if not station:
        return jsonify({'error': 'EV station not found'}), 404
    
    # 2차원 리스트: 충전기 그리드 배치
    chargers = []
    total_chargers = station.get('total', 4)
    rows = station.get('rows', 2)
    cols = station.get('cols', 2)
    # place_type과 place_id를 조합한 키로 충돌 방지
    reserved_key = f"ev:{station_id}"
    reserved = reserved_slots.get(reserved_key, set())
    
    for i in range(total_chargers):
        row = i // cols
        col = i % cols
        chargers.append({
            'id': i,
            'row': row,
            'col': col,
            'taken': i in reserved,
            'free': i not in reserved
        })
    
    station_detail = station.copy()
    station_detail['chargers'] = chargers
    station_detail['rows'] = rows
    station_detail['cols'] = cols
    
    return jsonify(station_detail)


# ============================================================================
# 예약 API
# ============================================================================

@app.route('/api/reservations', methods=['POST'])
@require_auth
@validate_required_fields('place_id', 'place_type', 'start_time', 'end_time', 'slot')
def create_reservation():
    """
    예약 생성
    Set 기반 중복 제거 - 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용
    """
    data = request.get_json()
    place_id = data['place_id']
    place_type = data['place_type']  # 'parking' or 'ev'
    slot = data['slot']
    start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
    end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
    
    # 주차장 또는 충전소 확인 (Dictionary 기반 조회(O(1)))
    place_data = None
    if place_type == 'parking':
        place_data = parking_spots.get(place_id)
        if not place_data:
            return jsonify({'error': 'Parking spot not found'}), 404
    elif place_type == 'ev':
        place_data = ev_stations.get(place_id)
        if not place_data:
            return jsonify({'error': 'EV station not found'}), 404
    else:
        return jsonify({'error': 'Invalid place type'}), 400
    
    # Set operations: 중복 체크 (이미 예약된 슬롯인지 확인)
    # place_type과 place_id를 조합한 키로 충돌 방지 (주차장과 충전소가 같은 ID를 가져도 충돌 없음)
    # 집합(set): 중복 없는 값의 모음 → 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용.
    # set operations(교집합/합집합/차집합) — 필터 기능(예: EV+빈자리+근처거리)에 응용 가능.
    reserved_key = f"{place_type}:{place_id}"
    if reserved_key not in reserved_slots:
        reserved_slots[reserved_key] = set()
    
    # Set 기반 중복 체크 - 이미 예약된 슬롯인지 확인
    if slot in reserved_slots[reserved_key]:
        return jsonify({'error': 'Slot already reserved'}), 400
    
    # 예약 생성
    reservation_id = get_next_id('reservation')
    reservation = {
        'id': reservation_id,
        'user_id': request.user_id,
        'place_id': place_id,
        'place_type': place_type,
        'slot': slot,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'created_at': datetime.now().isoformat()
    }
    
    reservations[reservation_id] = reservation
    reserved_slots[reserved_key].add(slot)
    
    # 가용성 업데이트
    place_data['available'] = max(0, place_data.get('available', 0) - 1)
    
    return jsonify(reservation), 201


@app.route('/api/reservations/<int:reservation_id>', methods=['GET'])
@require_auth
def get_reservation(reservation_id):
    """
    예약 상세 조회
    Dictionary 기반 조회(O(1)) - Reservation 빠른 조회 구조
    """
    reservation = reservations.get(reservation_id)
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    # 소유자 확인
    if reservation['user_id'] != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    return jsonify(reservation)


@app.route('/api/my-reservations', methods=['GET'])
@require_auth
def get_my_reservations():
    """
    내 예약 목록 조회
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    """
    # 리스트 컴프리헨션으로 내 예약 필터링
    # 리스트 컴프리헨션(list comprehension): 한 줄로 리스트 생성 → 더미데이터, id 목록, 필터링 결과 만드는 데 사용.
    # map / filter / reduce 대체: 리스트 컴프리헨션 + generator로 깔끔하게 데이터 변환/필터링 → 조회 결과 처리, 통계 계산 등에서 응용.
    my_reservations = [
        reservation for reservation in reservations.values()
        if reservation.get('user_id') == request.user_id
    ]
    
    # 예약 정보에 장소 정보 추가
    for reservation in my_reservations:
        place_id = reservation.get('place_id')
        place_type = reservation.get('place_type', 'parking')
        
        if place_type == 'parking':
            place_data = parking_spots.get(place_id)
        elif place_type == 'ev':
            place_data = ev_stations.get(place_id)
        else:
            place_data = None
        
        if place_data:
            reservation['place_name'] = place_data.get('name', '알 수 없음')
            reservation['place_address'] = place_data.get('address', '')
        else:
            reservation['place_name'] = '삭제된 장소'
            reservation['place_address'] = ''
    
    # 날짜순 정렬 (최신순)
    # 익명 함수(lambda): 한 줄짜리 작은 함수 → 정렬 기준, 간단 필터 조건에 사용.
    my_reservations.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify({
        'reservations': my_reservations,
        'count': len(my_reservations)
    })


@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
@require_auth
def cancel_reservation(reservation_id):
    """
    예약 취소
    Dictionary 기반 조회(O(1)) - Reservation 빠른 조회 구조
    """
    reservation = reservations.get(reservation_id)
    if not reservation:
        return jsonify({'error': 'Reservation not found'}), 404
    
    # 소유자 확인
    if reservation['user_id'] != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    # 예약 취소 처리
    place_id = reservation.get('place_id')
    place_type = reservation.get('place_type', 'parking')
    slot = reservation.get('slot')
    
    # 예약된 슬롯 해제
    reserved_key = f"{place_type}:{place_id}"
    if reserved_key in reserved_slots:
        reserved_slots[reserved_key].discard(slot)
    
    # 가용성 업데이트
    if place_type == 'parking':
        place_data = parking_spots.get(place_id)
    elif place_type == 'ev':
        place_data = ev_stations.get(place_id)
    else:
        place_data = None
    
    if place_data:
        place_data['available'] = min(
            place_data.get('total', 0),
            place_data.get('available', 0) + 1
        )
    
    # 예약 삭제
    del reservations[reservation_id]
    
    return jsonify({'message': 'Reservation cancelled'})


# ============================================================================
# 커뮤니티 API
# ============================================================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    게시글 목록
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    슬라이싱: 페이징, 일부 구간만 보여줄 때 재활용
    """
    # 페이징 파라미터
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort', 'date')  # 'date' or 'likes'
    
    # 리스트 컴프리헨션으로 게시글 목록 생성
    # 리스트(list): 순서 있는 가변 컬렉션 → 게시글 목록 저장
    post_list = list(posts.values())
    
    # 좋아요 수 업데이트 (Set operations: 중복 제거)
    # 집합(set): 중복 없는 값의 모음 → 이미 좋아요한 사용자 id 등 "중복 체크"에 사용.
    for post in post_list:
        likes_set = post_likes.get(post['id'], set())
        post['likes'] = len(likes_set)
    
    # 정렬: 좋아요 순 또는 날짜 순
    # 익명 함수(lambda): 한 줄짜리 작은 함수 → 정렬 기준, 간단 필터 조건에 사용.
    if sort_by == 'likes':
        post_list.sort(key=lambda x: (x.get('likes', 0), x.get('created_at', datetime.min)), reverse=True)
    else:
        post_list.sort(key=lambda x: x.get('created_at', datetime.min), reverse=True)
    
    # 현재 사용자 좋아요 상태 추가
    user_id = request.headers.get('X-User-Id', type=int)
    if user_id:
        for post in post_list:
            likes_set = post_likes.get(post['id'], set())
            post['is_liked'] = user_id in likes_set
    
    # 슬라이싱: 페이징, 일부 구간만 보여줄 때 재활용
    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = post_list[start:end]
    
    return jsonify({
        'posts': paginated_posts,
        'count': len(post_list),
        'page': page,
        'per_page': per_page
    })


@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """
    게시글 상세
    Dictionary 기반 조회(O(1)) - Post 빠른 조회 구조
    """
    post = posts.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # 조회수 증가
    post['views'] = post.get('views', 0) + 1
    
    # 좋아요 수 업데이트 (Set operations: 중복 제거)
    likes_set = post_likes.get(post_id, set())
    post['likes'] = len(likes_set)
    
    # 현재 사용자가 좋아요 했는지 확인
    user_id = request.headers.get('X-User-Id', type=int)
    post['is_liked'] = user_id in likes_set if user_id else False
    
    # 댓글 목록 가져오기 (리스트 컴프리헨션)
    # 리스트 컴프리헨션(list comprehension): 한 줄로 리스트 생성 → 더미데이터, id 목록, 필터링 결과 만드는 데 사용.
    post_comments = [c for c in comments.values() if c.get('post_id') == post_id]
    # 익명 함수(lambda): 한 줄짜리 작은 함수 → 정렬 기준, 간단 필터 조건에 사용.
    post_comments.sort(key=lambda x: x.get('created_at', datetime.min))
    
    post_detail = post.copy()
    post_detail['comments'] = post_comments
    
    return jsonify(post_detail)


@app.route('/api/posts', methods=['POST'])
@require_auth
@validate_required_fields('title', 'content')
def create_post():
    """
    게시글 작성
    Dictionary 기반 조회(O(1)) - Post 빠른 조회 구조
    """
    data = request.get_json()
    user = users.get(request.user_id)
    
    post_id = get_next_id('post')
    now = datetime.now()
    
    new_post = {
        'id': post_id,
        'title': data['title'],
        'content': data['content'],
        'author': user.get('name', '익명'),
        'author_id': request.user_id,
        'date': now.strftime('%m/%d'),
        'views': 0,
        'likes': 0,
        'created_at': now
    }
    
    posts[post_id] = new_post
    post_likes[post_id] = set()  # 좋아요 Set 초기화
    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@require_auth
def update_post(post_id):
    """
    게시글 수정
    Dictionary 기반 조회(O(1)) - Post 빠른 조회 구조
    """
    post = posts.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # 작성자 확인
    if post.get('author_id') != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    # 가변 객체(mutable object): 딕셔너리 내부 상태 변경
    # 가변 객체(mutable object): 리스트, 딕셔너리처럼 내부 상태 변경 가능 → 함수 기본값으로 쓰면 안 되는 타입.
    # dict comprehension — JSON 변환 시 빠르고 간결하게 response 구성 가능.
    post.update({k: v for k, v in data.items() if k not in ['id', 'author_id', 'created_at']})
    
    return jsonify(post)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@require_auth
def delete_post(post_id):
    """
    게시글 삭제
    Dictionary 기반 조회(O(1)) - Post 빠른 조회 구조
    """
    post = posts.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404
    
    # 작성자 확인
    if post.get('author_id') != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    del posts[post_id]
    
    # 관련 댓글도 삭제 (리스트 컴프리헨션)
    # 리스트 컴프리헨션(list comprehension): 한 줄로 리스트 생성 → 더미데이터, id 목록, 필터링 결과 만드는 데 사용.
    comment_ids_to_delete = [cid for cid, comment in comments.items() if comment.get('post_id') == post_id]
    # 슬라이스에 할당 / del: 슬라이싱을 이용해 중간 구간 삭제/치환 → 페이징 결과에서 특정 구간 제거, 다수 레코드 한번에 교체에 응용.
    for cid in comment_ids_to_delete:
        del comments[cid]
    
    return jsonify({'message': 'Post deleted'})


@app.route('/api/my-posts', methods=['GET'])
@require_auth
def get_my_posts():
    """
    내 게시글 목록
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    """
    # 리스트 컴프리헨션으로 내 게시글 필터링
    my_posts = [post for post in posts.values() if post.get('author_id') == request.user_id]
    return jsonify({'posts': my_posts, 'count': len(my_posts)})


@app.route('/api/posts/<int:post_id>/comments', methods=['POST'])
@require_auth
@validate_required_fields('content')
def create_comment(post_id):
    """
    댓글 작성
    Dictionary 기반 조회(O(1)) - Comment 빠른 조회 구조
    """
    if post_id not in posts:
        return jsonify({'error': 'Post not found'}), 404
    
    data = request.get_json()
    user = users.get(request.user_id)
    
    comment_id = get_next_id('comment')
    now = datetime.now()
    
    new_comment = {
        'id': comment_id,
        'post_id': post_id,
        'author': user.get('name', '익명'),
        'author_id': request.user_id,
        'content': data['content'],
        'date': now.strftime('%m/%d %H:%M'),
        'created_at': now
    }
    
    comments[comment_id] = new_comment
    return jsonify(new_comment), 201


@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
@require_auth
def toggle_like(post_id):
    """
    게시글 좋아요 토글
    Set 기반 중복 제거 - 이미 좋아요한 게시글인지 확인
    """
    if post_id not in posts:
        return jsonify({'error': 'Post not found'}), 404
    
    # Set operations: 중복 체크
    # 집합(set): 중복 없는 값의 모음 → 이미 좋아요한 사용자 id 등 "중복 체크"에 사용.
    # set operations(교집합/합집합/차집합) — 필터 기능(예: EV+빈자리+근처거리)에 응용 가능.
    if post_id not in post_likes:
        post_likes[post_id] = set()
    
    likes_set = post_likes[post_id]
    # Set 기반 중복 체크 - 이미 좋아요한 사용자인지 확인
    if request.user_id in likes_set:
        # 좋아요 취소
        likes_set.discard(request.user_id)
        is_liked = False
    else:
        # 좋아요 추가
        likes_set.add(request.user_id)
        is_liked = True
    
    # 좋아요 수 업데이트
    posts[post_id]['likes'] = len(likes_set)
    
    return jsonify({
        'is_liked': is_liked,
        'likes': len(likes_set)
    })


@app.route('/api/posts/popular', methods=['GET'])
def get_popular_posts():
    """
    인기 게시글 목록 (좋아요 순)
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    """
    limit = request.args.get('limit', 5, type=int)
    
    # 리스트 컴프리헨션으로 게시글 목록 생성
    post_list = list(posts.values())
    
    # 좋아요 수 업데이트 (Set operations: 중복 제거)
    for post in post_list:
        likes_set = post_likes.get(post['id'], set())
        post['likes'] = len(likes_set)
    
    # 좋아요 순으로 정렬
    post_list.sort(key=lambda x: (x.get('likes', 0), x.get('created_at', datetime.min)), reverse=True)
    
    # 상위 N개만 반환
    popular_posts = post_list[:limit]
    
    return jsonify({
        'posts': popular_posts,
        'count': len(popular_posts)
    })


# ============================================================================
# 충전소 등록 API
# ============================================================================

@app.route('/api/ev-stations', methods=['POST'])
@require_auth
@validate_required_fields('name', 'address')
def create_ev_station():
    """
    충전소 등록
    Dictionary 기반 조회(O(1)) - EVStation 빠른 조회 구조
    """
    data = request.get_json()
    station_id = get_next_id('ev_station')
    
    # 행렬 정보 (rows, cols) 추가
    rows = data.get('rows', 2)
    cols = data.get('cols', 2)
    total = data.get('total', rows * cols)
    
    new_station = {
        'id': station_id,
        'name': data['name'],
        'address': data['address'],
        'distance': data.get('distance', 0),
        'available': data.get('available', total),
        'total': total,
        'rows': rows,
        'cols': cols,
        'price_per_kwh': data.get('price_per_kwh', 200),
        'operating_hours': data.get('operating_hours', '24시간'),
        'image': data.get('image', ''),
        # 튜플(tuple): 순서 있지만 불변 → (위도, 경도), (id, 이름) 같은 변경되면 안 되는 묶음에 사용.
        # 불변 객체(immutable object): 튜플, 문자열처럼 변경 불가 → 안전하게 키, 캐시, dict 키로 사용.
        'latitude': data.get('latitude', 0),
        'longitude': data.get('longitude', 0),
        'description': data.get('description', ''),
        'owner_id': request.user_id
    }
    
    ev_stations[station_id] = new_station
    return jsonify(new_station), 201


@app.route('/api/my-ev-stations', methods=['GET'])
@require_auth
def get_my_ev_stations():
    """
    내 충전소 목록
    리스트 컴프리헨션: 필터링 결과 만드는 데 사용
    """
    # 리스트 컴프리헨션으로 내 충전소 필터링
    my_stations = [station for station in ev_stations.values() if station.get('owner_id') == request.user_id]
    return jsonify({'stations': my_stations, 'count': len(my_stations)})


@app.route('/api/ev-stations/<int:station_id>', methods=['PUT'])
@require_auth
def update_ev_station(station_id):
    """
    충전소 수정
    Dictionary 기반 조회(O(1)) - EVStation 빠른 조회 구조
    """
    station = ev_stations.get(station_id)
    if not station:
        return jsonify({'error': 'EV station not found'}), 404
    
    # 소유자 확인
    if station.get('owner_id') != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    data = request.get_json()
    # 가변 객체(mutable object): 딕셔너리 내부 상태 변경
    # 가변 객체(mutable object): 리스트, 딕셔너리처럼 내부 상태 변경 가능 → 함수 기본값으로 쓰면 안 되는 타입.
    # dict comprehension — JSON 변환 시 빠르고 간결하게 response 구성 가능.
    station.update({k: v for k, v in data.items() if k != 'id'})
    
    return jsonify(station)


@app.route('/api/ev-stations/<int:station_id>', methods=['DELETE'])
@require_auth
def delete_ev_station(station_id):
    """
    충전소 삭제
    Dictionary 기반 조회(O(1)) - EVStation 빠른 조회 구조
    """
    station = ev_stations.get(station_id)
    if not station:
        return jsonify({'error': 'EV station not found'}), 404
    
    # 소유자 확인
    if station.get('owner_id') != request.user_id:
        return jsonify({'error': 'Permission denied'}), 403
    
    del ev_stations[station_id]
    return jsonify({'message': 'EV station deleted'})


# ============================================================================
# 더미 데이터 초기화 함수 (시연용)
# ============================================================================

def init_dummy_data():
    """
    시연 영상용 더미 데이터 초기화
    """
    # admin 계정 생성
    admin_id = get_next_id('user')
    users[admin_id] = {
        'id': admin_id,
        'email': 'admin',
        'password': 'admin',
        'name': '관리자'
    }
    
    # 한밭대학교 좌표 (대략)
    hbnu_lat = 36.3733
    hbnu_lng = 127.3600
    
    # 대전 좌표들 (제공된 이미지에 맞춰 수정)
    daejeon_locations = [
        {'name': '대전역', 'lat': 36.3322, 'lng': 127.4342, 'address': '대전광역시 동구 동서대로 1689'},
        {'name': '둔산동', 'lat': 36.3504, 'lng': 127.3845, 'address': '대전광역시 서구 둔산로 100'},
        {'name': '현충원역', 'lat': 36.3600, 'lng': 127.3800, 'address': '대전광역시 유성구 현충원로'},
        {'name': '구암역', 'lat': 36.3650, 'lng': 127.3500, 'address': '대전광역시 유성구 구암로'},
        {'name': '대전 월드컵경기장', 'lat': 36.3200, 'lng': 127.4100, 'address': '대전광역시 유성구 월드컵대로 32'}
    ]
    
    # 1. 한밭대학교 N4 주차장 (4*3 = 12칸)
    spot1_id = get_next_id('parking_spot')
    parking_spots[spot1_id] = {
        'id': spot1_id,
        'name': '한밭대학교 N4 주차장',
        'address': '대전광역시 유성구 대학로 201',
        'distance': 0.5,
        'available': 10,  # 12칸 중 2칸 예약됨
        'total': 12,
        'rows': 4,
        'cols': 3,
        'price_per_hour': 1000,
        'operating_hours': '24시간',
        'image': 'https://www.hanbat.ac.kr/thumbnail/BBSMSTR_000000000058/920_BBS_201912101118547470.JPG',
        'is_ev': False,
        'latitude': hbnu_lat + 0.001,
        'longitude': hbnu_lng + 0.001,
        'description': '한밭대학교 N4 건물 인근 주차장입니다.',
        'owner_id': admin_id
    }
    
    # 2. 한밭대학교 N11 주차장 (5*3 = 15칸)
    spot2_id = get_next_id('parking_spot')
    parking_spots[spot2_id] = {
        'id': spot2_id,
        'name': '한밭대학교 N11 주차장',
        'address': '대전광역시 유성구 대학로 201',
        'distance': 0.3,
        'available': 12,  # 15칸 중 3칸 예약됨
        'total': 15,
        'rows': 5,
        'cols': 3,
        'price_per_hour': 1000,
        'operating_hours': '24시간',
        'image': 'https://www.hanbat.ac.kr/namo/binary/images/000173/%EA%B5%AD%EB%A6%BD%ED%95%9C%EB%B0%AD%EB%8C%80%ED%95%99%EA%B5%90_%EC%B0%BD%EC%9D%98%ED%98%81%EC%8B%A0%EA%B4%801.jpg',
        'is_ev': False,
        'latitude': hbnu_lat + 0.002,
        'longitude': hbnu_lng + 0.002,
        'description': '한밭대학교 N11 건물 인근 주차장입니다.',
        'owner_id': admin_id
    }
    
    # 3. 대전권 주차장 5개 (제공된 이미지에 맞춰 수정)
    daejeon_parking_data = [
        {'name': '대전역 주차장', 'rows': 3, 'cols': 4, 'image': 'https://mblogthumb-phinf.pstatic.net/MjAyMDAzMDRfOTEg/MDAxNTgzMzE2NzQ3Njk2.GUl5qod23OhwCfdO-qCCPImuSjAPH9jQaoCacPFCjdkg.642uESNWai-TYtzmNI2l6kRd_VS3yLtx1WH4vdCHvcYg.JPEG.korailblog/%EB%8C%80%EC%A0%84%EC%97%AD_%EA%B9%80%EC%9C%A4%EA%B2%BD_(1).jpg?type=w800'},
        {'name': '둔산동 공영주차장', 'rows': 3, 'cols': 4, 'image': 'https://cdn.goodmorningcc.com/news/photo/202003/228126_235093_3950.jpg'},
        {'name': '현충원역 주차장', 'rows': 4, 'cols': 3, 'image': 'https://mblogthumb-phinf.pstatic.net/MjAyMzA5MjBfMjI1/MDAxNjk1MjE2Mjk2OTg1.D8DRsQEHmxZykhErPMiveJO96hRN1qS4XUG5sk3MK30g.l2g1PFK3le_jL_EhCULEtj0Y2QAEMBFZoYNdYZFQ0iIg.JPEG.nono1831/output_1843831556.jpg?type=w800'},
        {'name': '구암역 주차장', 'rows': 4, 'cols': 3, 'image': 'https://cdn.welfarehello.com/naver-blog/production/yuseonggu/2025-02/223764460670/yuseonggu_223764460670_1.png?f=webp&q=80&w=800'},
        {'name': '대전 월드컵경기장 주차장', 'rows': 5, 'cols': 3, 'image': 'https://i.namu.wiki/i/d4RugJNwgw19u6tQ0fNecKrg_TiK4REZMlXTBUQ1c45hkHwKl5rQ_a6Dzkan4VKtabiFdZz3xIqGO1cRfMqvFw.webp'}
    ]
    
    for i, (loc, parking_data) in enumerate(zip(daejeon_locations, daejeon_parking_data)):
        spot_id = get_next_id('parking_spot')
        rows = parking_data['rows']
        cols = parking_data['cols']
        total = rows * cols
        parking_spots[spot_id] = {
            'id': spot_id,
            'name': parking_data['name'],
            'address': loc['address'],
            'distance': round(2.0 + i * 0.5, 1),
            'available': total - (i + 1),  # 몇 개 예약됨
            'total': total,
            'rows': rows,
            'cols': cols,
            'price_per_hour': 1000 + i * 200,
            'operating_hours': '24시간',
            'image': parking_data['image'],
            'is_ev': i == 1,  # 둔산동만 EV 가능
            'latitude': loc['lat'],
            'longitude': loc['lng'],
            'description': f'{loc["name"]} 인근 주차장입니다.',
            'owner_id': None  # admin 소유 아님
        }
    
    # 4. 한밭대학교 국제교류관 전기차 충전소 (4*1 = 4칸)
    ev1_id = get_next_id('ev_station')
    ev_stations[ev1_id] = {
        'id': ev1_id,
        'name': '한밭대학교 국제교류관 전기차 충전소',
        'address': '대전광역시 유성구 대학로 201',
        'distance': 0.2,
        'available': 2,  # 4칸 중 2칸 예약됨
        'total': 4,
        'rows': 4,
        'cols': 1,
        'price_per_kwh': 200,
        'operating_hours': '24시간',
        'image': 'https://www.hanbat.ac.kr/thumbnail/BBSMSTR_000000000058/920_BBS_201912090740019110.jpg',
        'latitude': hbnu_lat + 0.0005,
        'longitude': hbnu_lng + 0.0005,
        'description': '한밭대학교 국제교류관 앞 전기차 충전소입니다.',
        'owner_id': admin_id
    }
    
    # 5. 대전권 충전소 5개 (제공된 이미지에 맞춰 수정)
    daejeon_ev_data = [
        {'name': '대전국립중앙과학관 전기차 충전소', 'rows': 2, 'cols': 2, 'image': 'https://cdn.welfarehello.com/naver-blog/production/storydaejeon/2023-08/223179165734/storydaejeon_223179165734_1.jpg?f=webp&q=80&w=800', 'address': '대전광역시 유성구 대덕대로 481'},
        {'name': '현충원역 전기차 충전소', 'rows': 2, 'cols': 2, 'image': 'https://mblogthumb-phinf.pstatic.net/MjAyMzA5MjBfMjI1/MDAxNjk1MjE2Mjk2OTg1.D8DRsQEHmxZykhErPMiveJO96hRN1qS4XUG5sk3MK30g.l2g1PFK3le_jL_EhCULEtj0Y2QAEMBFZoYNdYZFQ0iIg.JPEG.nono1831/output_1843831556.jpg?type=w800', 'address': '대전광역시 유성구 현충원로'},
        {'name': '대전역 전기차 충전소', 'rows': 3, 'cols': 2, 'image': 'https://mblogthumb-phinf.pstatic.net/MjAyMDAzMDRfOTEg/MDAxNTgzMzE2NzQ3Njk2.GUl5qod23OhwCfdO-qCCPImuSjAPH9jQaoCacPFCjdkg.642uESNWai-TYtzmNI2l6kRd_VS3yLtx1WH4vdCHvcYg.JPEG.korailblog/%EB%8C%80%EC%A0%84%EC%97%AD_%EA%B9%80%EC%9C%A4%EA%B2%BD_(1).jpg?type=w800', 'address': '대전광역시 동구 동서대로 1689'},
        {'name': '구암역 전기차 충전소', 'rows': 2, 'cols': 2, 'image': 'https://cdn.welfarehello.com/naver-blog/production/yuseonggu/2025-02/223764460670/yuseonggu_223764460670_1.png?f=webp&q=80&w=800', 'address': '대전광역시 유성구 구암로'},
        {'name': '대전 월드컵경기장 전기차 충전소', 'rows': 2, 'cols': 2, 'image': 'https://i.namu.wiki/i/d4RugJNwgw19u6tQ0fNecKrg_TiK4REZMlXTBUQ1c45hkHwKl5rQ_a6Dzkan4VKtabiFdZz3xIqGO1cRfMqvFw.webp', 'address': '대전광역시 유성구 월드컵대로 32'}
    ]
    
    ev_locations = [
        {'lat': 36.3700, 'lng': 127.3450},  # 대전국립중앙과학관
        {'lat': 36.3600, 'lng': 127.3800},  # 현충원역
        {'lat': 36.3322, 'lng': 127.4342},  # 대전역
        {'lat': 36.3650, 'lng': 127.3500},  # 구암역
        {'lat': 36.3200, 'lng': 127.4100}   # 대전 월드컵경기장
    ]
    
    for i, (ev_data, ev_loc) in enumerate(zip(daejeon_ev_data, ev_locations)):
        ev_id = get_next_id('ev_station')
        rows = ev_data['rows']
        cols = ev_data['cols']
        total = rows * cols
        ev_stations[ev_id] = {
            'id': ev_id,
            'name': ev_data['name'],
            'address': ev_data['address'],
            'distance': round(1.5 + i * 0.4, 1),
            'available': total - (i % 2),  # 몇 개 예약됨
            'total': total,
            'rows': rows,
            'cols': cols,
            'price_per_kwh': 180 + i * 20,
            'operating_hours': '24시간',
            'image': ev_data['image'],
            'latitude': ev_loc['lat'],
            'longitude': ev_loc['lng'],
            'description': f'{ev_data["name"]}입니다.',
            'owner_id': None  # admin 소유 아님
        }
    
    # 6. 예약 데이터 생성 (admin 계정 예약 2~3개만)
    # N4 주차장 예약 2개
    reserved_key1 = f"parking:{spot1_id}"
    reserved_slots[reserved_key1] = {0, 5}  # 2개 슬롯 예약
    for slot in [0, 5]:
        res_id = get_next_id('reservation')
        start_time = datetime.now() + timedelta(hours=1)
        end_time = start_time + timedelta(hours=2)
        reservations[res_id] = {
            'id': res_id,
            'user_id': admin_id,
            'place_id': spot1_id,
            'place_type': 'parking',
            'slot': slot,
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'created_at': datetime.now().isoformat()
        }
    
    # 국제교류관 충전소 예약 1개
    reserved_key3 = f"ev:{ev1_id}"
    reserved_slots[reserved_key3] = {1}  # 1개 슬롯 예약
    res_id = get_next_id('reservation')
    start_time = datetime.now() + timedelta(hours=3)
    end_time = start_time + timedelta(hours=1)
    reservations[res_id] = {
        'id': res_id,
        'user_id': admin_id,
        'place_id': ev1_id,
        'place_type': 'ev',
        'slot': 1,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'created_at': datetime.now().isoformat()
    }
    
    # N4 주차장 available 업데이트 (3칸 -> 2칸 예약)
    parking_spots[spot1_id]['available'] = 10  # 12칸 중 2칸 예약됨
    # 국제교류관 충전소 available 업데이트 (2칸 -> 1칸 예약)
    ev_stations[ev1_id]['available'] = 3  # 4칸 중 1칸 예약됨
    
    # 7. admin 즐겨찾기 추가
    favorites[admin_id] = {spot1_id, spot2_id, ev1_id}
    
    # 8. 커뮤니티 게시글 20개
    post_titles = [
        '한밭대 주차장 추천합니다!',
        'N4 주차장 이용 후기',
        '전기차 충전소 위치 공유',
        '주차 요금 너무 비싸네요',
        '주차장 찾기 어려워요',
        'EV 충전소 이용 팁',
        '한밭대 주변 주차장 정보',
        '주차 예약 시스템 사용법',
        '전기차 충전 시간은 얼마나 걸리나요?',
        '주차장 혼잡도 체크 방법',
        'N11 주차장 추천해요',
        '국제교류관 충전소 후기',
        '주차장 예약 취소 방법',
        '대전역 주변 주차장 추천',
        '전기차 충전 요금 비교',
        '주차장 이용 시 주의사항',
        '한밭대 학생 할인 혜택',
        '주차장 찾는 팁',
        'EV 충전소 이용 후기',
        '주차 예약 시스템 개선 제안'
    ]
    
    post_contents = [
        '한밭대학교 주변 주차장을 이용해보니 정말 편리하네요!',
        'N4 주차장은 접근성이 좋고 가격도 합리적입니다.',
        '전기차 충전소 위치를 공유합니다. 참고하세요!',
        '주차 요금이 좀 비싼 것 같아요. 다른 곳은 어떤가요?',
        '주차장을 찾기가 너무 어려워요. 안내가 필요합니다.',
        'EV 충전소 이용 시 충전 시간은 보통 30분~1시간 정도 걸립니다.',
        '한밭대 주변 주차장 정보를 정리해봤습니다.',
        '주차 예약 시스템 사용법을 알려드립니다.',
        '전기차 충전 시간은 배터리 용량과 충전 속도에 따라 다릅니다.',
        '주차장 혼잡도는 실시간으로 확인할 수 있습니다.',
        'N11 주차장을 추천합니다. 넓고 깨끗해요!',
        '국제교류관 충전소는 접근성이 좋습니다.',
        '주차장 예약 취소는 앱에서 간단하게 할 수 있습니다.',
        '대전역 주변 주차장 중 추천할 만한 곳이 있나요?',
        '전기차 충전 요금을 비교해봤습니다.',
        '주차장 이용 시 주의사항을 공유합니다.',
        '한밭대 학생은 할인 혜택을 받을 수 있습니다.',
        '주차장을 쉽게 찾는 팁을 알려드립니다.',
        'EV 충전소 이용 후기를 공유합니다.',
        '주차 예약 시스템 개선 제안을 드립니다.'
    ]
    
    for i in range(20):
        post_id = get_next_id('post')
        now = datetime.now() - timedelta(days=i, hours=i % 24)
        views = 10 + i * 5 + (i % 3) * 10  # 조회수 다양하게
        likes_count = i % 7  # 좋아요 수 다양하게
        
        posts[post_id] = {
            'id': post_id,
            'title': post_titles[i],
            'content': post_contents[i],
            'author': '관리자' if i < 5 else f'사용자{i-4}',
            'author_id': admin_id if i < 5 else None,
            'date': now.strftime('%m/%d'),
            'views': views,
            'likes': likes_count,
            'created_at': now
        }
        
        # 좋아요 데이터 생성
        if likes_count > 0:
            post_likes[post_id] = set()
            # admin이 일부 좋아요
            if i % 3 == 0:
                post_likes[post_id].add(admin_id)
                likes_count -= 1
            # 가상의 사용자들이 좋아요
            for j in range(likes_count):
                post_likes[post_id].add(100 + j)  # 가상 사용자 ID
    
    print("더미 데이터 초기화 완료!")
    print(f"Admin 계정: id={admin_id}, email=admin, password=admin")
    print(f"주차장: {len(parking_spots)}개")
    print(f"충전소: {len(ev_stations)}개")
    print(f"게시글: {len(posts)}개")
    print(f"예약: {len(reservations)}개")


# ============================================================================
# 애플리케이션 초기화
# ============================================================================

# 시연용 더미 데이터 초기화
    init_dummy_data()
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)

