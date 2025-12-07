# 🧩 OSS 2025-2 — PlinkU 주차 문제 해결 플랫폼

**Backend & Frontend Monorepo README**

PlinkU는 OSS 2025-2 수업을 위해 설계된 **주차장 안내 + EV 충전소 + 마켓플레이스 + 커뮤니티 플랫폼**입니다.
백엔드는 Flask 기반 REST API로 구성되어 있으며, 프론트는 HTML/CSS/JS(React CDN 기반) SPA 구조로 구성됩니다.

이 문서는 **전체 레포지토리의 통합 문서**로서 설치, 실행, API, 기술 스택, 구현된 알고리즘, 브랜치 전략, 기여자 등을 하나로 정리한 README입니다.

PlinkU는 **[http://18.191.185.124](http://18.191.185.124)** 에서 호스팅되어 있습니다.

---

## 📘 프로젝트 개요

PlinkU 플랫폼은 다음 기능을 제공합니다:

### 🔐 사용자 인증

- 회원가입 / 로그인 / 로그아웃

### 🚗 주차장 안내

- 주차장 목록/상세 조회
- 주차장 등록, 수정, 삭제
- 사용자 소유 주차장 관리
- 슬롯 단위 예약 가능

### 🔌 전기차 충전소 안내

- 충전소 목록/상세
- 충전소 등록, 수정, 삭제
- 슬롯 단위 예약 가능

### ⭐ 즐겨찾기

- 주차장·충전소 즐겨찾기 추가/삭제
- 즐겨찾기 자동 그룹화

### 🧾 예약

- 주차장·EV 충전 슬롯 예약
- 예약 상세 조회
- 내 예약 목록 조회
- 예약 취소

### 📝 커뮤니티

- 게시글 CRUD (작성, 조회, 수정, 삭제)
- 내 게시글 관리
- 댓글 작성
- 좋아요 기능
- 인기 게시글 정렬
- 조회수, 날짜, 좋아요 기반 필터
- 페이지네이션 지원

---

## ⚙️ 기술 스택

### Backend (Flask)

| 분류      | 기술                              |
| --------- | --------------------------------- |
| Language  | Python 3.12                       |
| Framework | Flask                             |
| DB        | SQLite 설계, 현재는 인메모리 구조 |
| ORM       | SQLAlchemy(추가 예정)             |
| Auth      | JWT 예정, 현재는 X-User-Id 인증   |
| API       | RESTful                           |

> Backend 의존성: `requirements.txt` 참고

---

### Frontend

| 분류       | 기술                                        |
| ---------- | ------------------------------------------- |
| UI         | HTML + CSS                                  |
| 라이브러리 | React 18 (CDN), Material Icons              |
| 구조       | SPA (Single Page Application)               |
| 네비게이션 | 스택 기반 라우팅 (뒤로가기 기능)            |
| 스타일     | Apple SD Gothic Neo 기반 전체 커스텀 디자인 |
| API 통신   | Fetch API, CORS 지원                        |

> 전체 스타일 정의: `FE/styles.css` 참고  
> 프론트엔드 코드: `FE/index.html` (React CDN 기반, Babel Standalone 사용)

---

## 📂 프로젝트 구조

```
/plinku-ec2-deploy
 ├── BE/
 │   ├── main.py           # Flask REST API 서버 (메인 엔트리 포인트, 모든 API 구현)
 │   ├── requirements.txt  # 백엔드 의존성 (Flask, Flask-CORS, gunicorn)
 │   ├── Dockerfile        # 백엔드 Docker 이미지 빌드 파일
 │   ├── instance/         # SQLite 데이터베이스 저장 디렉토리
 │   └── app/              # 애플리케이션 모듈 디렉토리 (현재 미사용)
 ├── FE/
 │   ├── index.html        # Frontend SPA 엔트리 파일 (React CDN 기반)
 │   ├── styles.css        # UI 전체 스타일 (Apple SD Gothic Neo 폰트)
 │   ├── Dockerfile        # 프론트엔드 Docker 이미지 빌드 파일
 │   └── README.md         # 프론트엔드 README
 └── docker-compose.yml    # Docker Compose 설정 파일 (백엔드:8000, 프론트:80)
```

---

## 🚀 백엔드 설치 및 실행

### 1. 가상환경 생성 (선택)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치

```bash
cd BE
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
cd BE
python main.py
```

서버는 기본적으로 `http://localhost:5000`에서 실행됩니다.

> **참고**: 서버 실행 시 `init_dummy_data()` 함수가 자동으로 실행되어 시연용 더미 데이터가 생성됩니다.
>
> - Admin 계정: `admin` / `admin`
> - 주차장 7개, 충전소 6개
> - 게시글 20개
> - 예약 데이터 포함

### 4. Docker Compose를 사용한 실행 (권장)

프로젝트 루트에서:

```bash
docker-compose up -d
```

- 백엔드: `http://localhost:8000`
- 프론트엔드: `http://localhost:80`

### 5. 프론트엔드 개발 서버 실행 (선택)

프론트엔드를 별도로 실행하려면:

```bash
cd FE
# 간단한 HTTP 서버 실행 (Python 3)
python -m http.server 3000
```

프론트엔드는 `http://localhost:3000`에서 실행됩니다.

> **참고**: 프론트엔드의 API_BASE는 `http://localhost:5000`으로 설정되어 있습니다. (`index.html` 37번째 줄)

---

## 📡 API 엔드포인트 요약

백엔드 전체 API 구현은 `BE/main.py` 참고:

> **참고**: 모든 API는 `/api/` 접두사를 사용하며, 인증이 필요한 API는 `X-User-Id` 헤더를 요구합니다.

---

### 🔐 인증 API

| METHOD | URL         | 설명      | 인증 필요 |
| ------ | ----------- | --------- | --------- |
| GET    | /api/health | 헬스 체크 | ❌        |
| POST   | /api/signup | 회원가입  | ❌        |
| POST   | /api/login  | 로그인    | ❌        |
| POST   | /api/logout | 로그아웃  | ❌        |

---

### 🚗 주차장 API

| METHOD | URL                    | 설명           | 인증 필요 |
| ------ | ---------------------- | -------------- | --------- |
| GET    | /api/parking-spots     | 주차장 목록    | ❌        |
| GET    | /api/parking-spots/:id | 주차장 상세    | ❌        |
| POST   | /api/parking-spots     | 주차장 등록    | ✅        |
| PUT    | /api/parking-spots/:id | 주차장 수정    | ✅        |
| DELETE | /api/parking-spots/:id | 주차장 삭제    | ✅        |
| GET    | /api/my-parking-spots  | 내 소유 주차장 | ✅        |

---

### ⭐ 즐겨찾기 API

| METHOD | URL                | 설명          | 인증 필요 |
| ------ | ------------------ | ------------- | --------- |
| GET    | /api/favorites     | 즐겨찾기 목록 | ✅        |
| POST   | /api/favorites/:id | 즐겨찾기 추가 | ✅        |
| DELETE | /api/favorites/:id | 즐겨찾기 삭제 | ✅        |

---

### 🔌 EV 충전소 API

| METHOD | URL                  | 설명        | 인증 필요 |
| ------ | -------------------- | ----------- | --------- |
| GET    | /api/ev-stations     | 충전소 목록 | ❌        |
| GET    | /api/ev-stations/:id | 충전소 상세 | ❌        |
| POST   | /api/ev-stations     | 충전소 등록 | ✅        |
| PUT    | /api/ev-stations/:id | 충전소 수정 | ✅        |
| DELETE | /api/ev-stations/:id | 충전소 삭제 | ✅        |
| GET    | /api/my-ev-stations  | 내 충전소   | ✅        |

---

### 🧾 예약 API

| METHOD | URL                   | 설명         |
| ------ | --------------------- | ------------ |
| POST   | /api/reservations     | 예약 생성    |
| GET    | /api/reservations/:id | 예약 조회    |
| GET    | /api/my-reservations  | 내 예약 목록 |
| DELETE | /api/reservations/:id | 예약 취소    |

---

### 📝 커뮤니티 API

| METHOD | URL                     | 설명             | 인증 필요 |
| ------ | ----------------------- | ---------------- | --------- |
| GET    | /api/posts              | 게시글 목록      | ❌        |
| GET    | /api/posts/:id          | 게시글 상세      | ❌        |
| POST   | /api/posts              | 게시글 작성      | ✅        |
| PUT    | /api/posts/:id          | 게시글 수정      | ✅        |
| DELETE | /api/posts/:id          | 게시글 삭제      | ✅        |
| GET    | /api/my-posts           | 내 게시글 목록   | ✅        |
| POST   | /api/posts/:id/comments | 댓글 작성        | ✅        |
| POST   | /api/posts/:id/like     | 좋아요 토글      | ✅        |
| GET    | /api/posts/popular      | 인기 게시글 목록 | ❌        |

---

## 🧠 구현된 자료구조 & 알고리즘

아래 기능들은 모두 `main.py`에 구현되어 있으며, 각 자료구조의 활용 목적과 이점이 코드 주석으로 상세히 설명되어 있습니다.

### 1) Dictionary 기반 빠른 조회(O(1))

**해시 기반 조회(O(1))** — ParkingSpot, User 등 빠른 조회 구조 설계에 유리.

- `parking_spots: Dict[int, Dict]` - 주차장 ID 기반 O(1) 조회
- `users: Dict[int, Dict]` - 사용자 ID 기반 O(1) 조회
- `ev_stations: Dict[int, Dict]` - 충전소 ID 기반 O(1) 조회
- `reservations: Dict[int, Dict]` - 예약 ID 기반 O(1) 조회
- `posts: Dict[int, Dict]` - 게시글 ID 기반 O(1) 조회
- `comments: Dict[int, Dict]` - 댓글 ID 기반 O(1) 조회

**dict comprehension** — JSON 변환 시 빠르고 간결하게 response 구성 가능.

### 2) Set 기반 중복 체크 및 집합 연산

**중복 제거(set)** — 주차장 타입, EV 여부 필터 등에서 중복 없는 집합 처리 시 유용.

- `favorites: Dict[int, Set[int]]` - 사용자별 즐겨찾기 집합 (중복 자동 제거)
- `blocked_users: Set[int]` - 차단된 유저 ID 집합
- `reserved_slots: Dict[str, Set[int]]` - 예약된 슬롯 집합 (중복 체크)
- `post_likes: Dict[int, Set[int]]` - 게시글별 좋아요한 사용자 집합

**set operations(교집합/합집합/차집합)** — 필터 기능(예: EV+빈자리+근처거리)에 응용 가능.

### 3) Sequence 기반 구조 (리스트 동작 최적화)

**`__getitem__`으로 반복 가능 객체 만들기** — DB 모델 결과를 커스텀 리스트처럼 만들 수 있음.

**슬라이싱 지원** — Pagination 내부 구조를 커스텀 시퀀스로 구현 가능.

**`__contains__` 오버라이드** — 특정 ID 포함 여부 같은 로직 최적화 가능.

- `ParkingSpotList` 클래스
  - `__getitem__`: 인덱스로 바로 접근 가능한 연속 메모리 리스트처럼 동작
  - `__contains__`: 특정 ID 포함 여부 같은 로직 최적화
  - 슬라이싱 지원: 페이징 결과에서 특정 구간만 반환

### 4) 파이썬 기본 자료형 / 시퀀스 계열

**리스트(list)**: 순서 있는 가변 컬렉션 → 주차장 목록, 댓글 목록, 즐겨찾기 리스트 저장.

**튜플(tuple)**: 순서 있지만 불변 → (위도, 경도), (id, 이름) 같은 변경되면 안 되는 묶음에 사용.

**딕셔너리(dict)**: key → value 매핑 → 주차장 한 개의 상세 정보(이름, 가격, 좌표 등)를 한 번에 표현.

**집합(set)**: 중복 없는 값의 모음 → 이미 예약된 차량번호, 차단된 유저 id 등 "중복 체크"에 사용.

**2차원 리스트**: 리스트 안에 리스트 → 주차구역 그리드, 좌석/구획 배치 같은 표 형태 데이터.

**리스트 컴프리헨션(list comprehension)**: 한 줄로 리스트 생성 → 더미데이터, id 목록, 필터링 결과 만드는 데 사용.

**슬라이싱(slicing)**: `list[a:b]` 잘라 쓰기 → 페이징, 일부 구간만 보여줄 때 재활용.

### 5) 객체 참조 / 가변성 / 재활용

**가변 객체(mutable object)**: 리스트, 딕셔너리처럼 내부 상태 변경 가능 → 함수 기본값으로 쓰면 안 되는 타입.

**불변 객체(immutable object)**: 튜플, 문자열처럼 변경 불가 → 안전하게 키, 캐시, dict 키로 사용.

### 6) 퍼스트 클래스 함수 / 함수형 요소

**일급 객체(first-class function)**: 함수를 변수처럼 저장, 인자로 넘기고, 반환값으로 돌려줄 수 있음 → 전략 함수, 콜백, 훅 구현에 핵심.

**고차 함수(higher-order function)**: 함수를 받거나 반환하는 함수 → 공통 로직 래핑, 미들웨어 느낌으로 사용.

**익명 함수(lambda)**: 한 줄짜리 작은 함수 → 정렬 기준, 간단 필터 조건에 사용.

**callable 객체**: `__call__` 가진 클래스 인스턴스 → "함수처럼 행동하는 객체" 만들어서 상태+로직 묶을 때 사용.

**map / filter / reduce 대체**: 리스트 컴프리헨션 + generator로 깔끔하게 데이터 변환/필터링 → 조회 결과 처리, 통계 계산 등에서 응용.

### 7) 데코레이터 / 클로저

**클로저(closure)**: 함수 안에서 외부 변수 캡처해서 상태를 기억하는 함수 → 간단한 캐시, 카운터, 설정이 들어간 함수 만들 때 사용.

**nonlocal**: 클로저 내부에서 바깥 스코프 변수 수정할 때 쓰는 키워드.

**함수 데코레이터(function decorator)**: 다른 함수를 감싸서 기능을 추가하는 함수 → 인증 체크, 로깅, 실행 시간 측정, 트랜잭션 처리 같은 공통 기능에 바로 적용 가능.

- `@require_auth` - 인증 체크 데코레이터
- `@validate_required_fields` - 필드 검증 데코레이터

**등록용 데코레이터(registration decorator)**: 어떤 함수들을 자동으로 레지스트리에 모아두는 패턴 → "이벤트 핸들러 목록", "프로모션 전략 목록"처럼 플러그인 모으는 데 사용.

### 8) 스택 / 큐

**스택(Stack)**: LIFO 구조 → 이전 페이지/이전 검색 조건 되돌리기(undo), 깊이우선 탐색 같은 데 사용.

- 프론트엔드: `navigationStack` - React Router의 네비게이션 히스토리 스택 (뒤로가기 기능 구현)
- 백엔드: `navigation_stack: List[Dict]` - 네비게이션 히스토리 스택 (참고용)

**함수 호출 스택 개념**: 재귀, 예외 처리, 콜 스택 이해에 필요 → 복잡한 재귀 알고리즘 디버깅할 때 머릿속 모델.

**큐(Queue)**: FIFO 구조 → 예약 처리 대기열, 알림 발송 대기열, 비동기 작업 큐 개념을 이해하는 데 사용.

**우선순위 큐(Priority Queue)**: 우선순위 높은 작업 먼저 처리 → 예) 혼잡도 높은 주차장/긴급 요청 먼저 처리하는 로직에 응용 가능.

- `priority_queue` (heapq 기반) - 우선순위 작업 큐

### 9) 시퀀스 관련 실수/주의 포인트

**슬라이스에 할당 / del**: 슬라이싱을 이용해 중간 구간 삭제/치환 → 페이징 결과에서 특정 구간 제거, 다수 레코드 한번에 교체에 응용.

---

## 🎯 주요 기능 상세

### 프론트엔드 기능

- **스택 기반 네비게이션**: 뒤로가기 버튼이 스택을 사용하여 이전 페이지로 이동 (LIFO 구조)
- **반응형 디자인**: 모바일/데스크톱 대응
- **실시간 UI 업데이트**: API 호출 후 자동 리프레시
- **에러 처리**: 사용자 친화적인 에러 메시지 표시
- **로딩 상태 표시**: 비동기 작업 중 로딩 인디케이터
- **페이지네이션**: 커뮤니티 게시글 목록 페이징 지원
- **즐겨찾기 UI**: 주황색(#ff6b35) 별 아이콘으로 표시

### 백엔드 기능

- **시연용 더미 데이터**: 서버 시작 시 자동 생성 (`init_dummy_data()`)
  - Admin 계정: `admin` / `admin`
  - 주차장 7개 (한밭대 N4, N11 포함)
  - 충전소 6개 (한밭대 국제교류관 포함)
  - 게시글 20개 (좋아요, 조회수 포함)
  - 예약 데이터 3개
- **인메모리 데이터 저장**: Dictionary/Set 기반 빠른 조회
- **데코레이터 기반 인증**: `@require_auth`, `@validate_required_fields`
- **CORS 지원**: 프론트엔드와의 통신을 위한 CORS 설정

---

## 🧾 커밋 컨벤션

### 형식

```
type: subject
body
footer
```

### Commit Type

| 타입     | 설명           |
| -------- | -------------- |
| feat     | 새로운 기능    |
| fix      | 버그 수정      |
| docs     | 문서 변경      |
| style    | 포맷 변경      |
| refactor | 코드 개선      |
| test     | 테스트 추가    |
| chore    | 빌드/환경 작업 |

### Subject 규칙

- 50자 이하
- 마침표 X
- 개조식 구문

### Body 규칙

- 무엇을 / 왜 변경했는지 상세 기술

### Footer 예시

```
Resolves: #123
Ref: #45
Related to: #90, #99
```

---

## 🌿 브랜치 전략

| 브랜치         | 설명             |
| -------------- | ---------------- |
| main           | 배포 안정 버전   |
| develop        | 통합 개발 브랜치 |
| feature/기능명 | 신규 기능 개발   |
| fix/이슈명     | 버그 수정 브랜치 |

---

## 👥 기여자

### Backend

| 이름     | 역할                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------- |
| 김성민   | 주차장·충전소 등록/조회 API 개발, 예약 관련 API 개발, EC2·Docker를 통한 배포                            |
| 임민우   | 즐겨찾기 등록/삭제/조회 API 개발, 커뮤니티 게시글 CRUD API 개발                                         |
| 정용성   | 각종 테이블 설계, API 명세서 작성, Swagger 문서화                                                       |
| 예다은\* | 팀 총괄 및 협업 방향 제시, 프로토 타입 디자인 구성, React 기반 UI/UX 개발, 백엔드 API 전반 개발 및 연동 |
| 황인상   | 프로토 타입 디자인 구성, React 기반 UI/UX 개발, 시스템 아키텍처 설계                                    |
