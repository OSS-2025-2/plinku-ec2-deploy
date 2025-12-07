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

* 회원가입 / 로그인 / 로그아웃

### 🚗 주차장 안내

* 주차장 목록/상세 조회
* 주차장 등록, 수정, 삭제
* 사용자 소유 주차장 관리
* 슬롯 단위 예약 가능

### 🔌 전기차 충전소 안내

* 충전소 목록/상세
* 충전소 등록, 수정, 삭제
* 슬롯 단위 예약 가능

### ⭐ 즐겨찾기

* 주차장·충전소 즐겨찾기 추가/삭제
* 즐겨찾기 자동 그룹화

### 🧾 예약

* 주차장·EV 충전 슬롯 예약
* 예약 상세 조회

### 📝 커뮤니티

* 게시글 CRUD
* 댓글 작성
* 좋아요 기능
* 인기 게시글 정렬
* 조회수, 날짜, 좋아요 기반 필터

---

## ⚙️ 기술 스택

### Backend (Flask)

| 분류        | 기술                       |
| --------- | ------------------------ |
| Language  | Python 3.12              |
| Framework | Flask                    |
| DB        | SQLite 설계, 현재는 인메모리 구조   |
| ORM       | SQLAlchemy(추가 예정)        |
| Auth      | JWT 예정, 현재는 X-User-Id 인증 |
| API       | RESTful                  |

> Backend 의존성: `requirements.txt` 참고

---

### Frontend

| 분류    | 기술                                |
| ----- | --------------------------------- |
| UI    | HTML + CSS                        |
| 라이브러리 | React 18 (CDN), Material Icons    |
| 구조    | SPA                               |
| 스타일   | Apple SD Gothic Neo 기반 전체 커스텀 디자인 |

> 전체 스타일 정의: `styles.css` 참고

---

## 📂 프로젝트 구조

```
/BE
 ├── app.py                # Flask REST API 서버
 ├── requirements.txt      # 백엔드 의존성

/FE
 ├── index.html            # Frontend SPA 엔트리 파일
 ├── styles.css            # UI 전체 스타일           
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
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
python app.py
```

---

## 📡 API 엔드포인트 요약

백엔드 전체 API 구현은 `app.py` 참고:

---

### 🔐 인증 API

| METHOD | URL         | 설명   |
| ------ | ----------- | ---- |
| POST   | /api/signup | 회원가입 |
| POST   | /api/login  | 로그인  |
| POST   | /api/logout | 로그아웃 |

---

### 🚗 주차장 API

| METHOD | URL                    | 설명       |
| ------ | ---------------------- | -------- |
| GET    | /api/parking-spots     | 주차장 목록   |
| GET    | /api/parking-spots/:id | 주차장 상세   |
| POST   | /api/parking-spots     | 주차장 등록   |
| PUT    | /api/parking-spots/:id | 주차장 수정   |
| DELETE | /api/parking-spots/:id | 주차장 삭제   |
| GET    | /api/my-parking-spots  | 내 소유 주차장 |

---

### ⭐ 즐겨찾기 API

| METHOD | URL                | 설명      |
| ------ | ------------------ | ------- |
| GET    | /api/favorites     | 즐겨찾기 목록 |
| POST   | /api/favorites/:id | 즐겨찾기 추가 |
| DELETE | /api/favorites/:id | 즐겨찾기 삭제 |

---

### 🔌 EV 충전소 API

| METHOD | URL                  | 설명     |
| ------ | -------------------- | ------ |
| GET    | /api/ev-stations     | 충전소 목록 |
| GET    | /api/ev-stations/:id | 충전소 상세 |
| POST   | /api/ev-stations     | 충전소 등록 |
| PUT    | /api/ev-stations/:id | 충전소 수정 |
| DELETE | /api/ev-stations/:id | 충전소 삭제 |
| GET    | /api/my-ev-stations  | 내 충전소  |

---

### 🧾 예약 API

| METHOD | URL                   | 설명    |
| ------ | --------------------- | ----- |
| POST   | /api/reservations     | 예약 생성 |
| GET    | /api/reservations/:id | 예약 조회 |

---

### 📝 커뮤니티 API

| METHOD | URL                     | 설명        |
| ------ | ----------------------- | --------- |
| GET    | /api/posts              | 게시글 목록    |
| GET    | /api/posts/:id          | 게시글 상세    |
| POST   | /api/posts              | 게시글 작성    |
| PUT    | /api/posts/:id          | 게시글 수정    |
| DELETE | /api/posts/:id          | 게시글 삭제    |
| GET    | /api/my-posts           | 내 게시글 목록  |
| POST   | /api/posts/:id/comments | 댓글 작성     |
| POST   | /api/posts/:id/like     | 좋아요 토글    |
| GET    | /api/posts/popular      | 인기 게시글 목록 |

---

## 🧠 구현된 자료구조 & 알고리즘

아래 기능들은 모두 `app.py` 에 구현되어 있습니다.

### 1) Dictionary 기반 빠른 조회(O(1))

* parking_spots, users, ev_stations 등
  → ID 기반 O(1) 조회

### 2) Set 기반 중복 체크

* favorites
* reserved_slots(예약된 슬롯)
  → 교집합, 차집합 연산으로 최적화

### 3) Sequence 기반 구조

* ParkingSpotList
  → `__getitem__`, `__contains__`, 슬라이싱 지원
  → Pagination 및 필터 성능 향상

### 4) 함수형 요소 & 데코레이터

* `@require_auth` 인증 데코레이터
* `@validate_required_fields` 필드 검증
* 클로저 기반 인증 래핑
* 고차 함수 기반 미들웨어 구조

### 5) 자료구조 활용 패턴

* 리스트: 목록·필터링·페이징
* 튜플: (latitude, longitude) 좌표
* 2차원 리스트: 주차장/충전소 슬롯 그리드
* 우선순위 큐(heapq): 이벤트 처리

---

## 🧾 커밋 컨벤션

### 형식

```
type: subject
body
footer
```

### Commit Type

| 타입       | 설명       |
| -------- | -------- |
| feat     | 새로운 기능   |
| fix      | 버그 수정    |
| docs     | 문서 변경    |
| style    | 포맷 변경    |
| refactor | 코드 개선    |
| test     | 테스트 추가   |
| chore    | 빌드/환경 작업 |

### Subject 규칙

* 50자 이하
* 마침표 X
* 개조식 구문

### Body 규칙

* 무엇을 / 왜 변경했는지 상세 기술

### Footer 예시

```
Resolves: #123
Ref: #45
Related to: #90, #99
```

---

## 🌿 브랜치 전략

| 브랜치         | 설명        |
| ----------- | --------- |
| main        | 배포 안정 버전  |
| develop     | 통합 개발 브랜치 |
| feature/기능명 | 신규 기능 개발  |
| fix/이슈명     | 버그 수정 브랜치 |

---

## 👥 기여자

### Backend

| 이름  | 역할     |
| --- | ------ |
| 김성민 | 주차장·충전소 등록/조회 API 개발, 예약 관련 API 개발, EC2·Docker를 통한 배포 |
| 임민우 | 즐겨찾기 등록/삭제/조회 API 개발, 커뮤니티 게시글 CRUD API 개발 |
| 정용성 | 각종 테이블 설계, API 명세서 작성, Swagger 문서화 |
| 예다은* | 팀 총괄 및 협업 방향 제시, 프로토 타입 디자인 구성, React 기반 UI/UX 개발, 백엔드 API 전반 개발 및 연동 |
| 황인상 | 프로토 타입 디자인 구성, React 기반 UI/UX 개발, 시스템 아키텍처 설계|
