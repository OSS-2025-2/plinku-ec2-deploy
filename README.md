# 🧩 OSS 2025-2 주차 문제 해결 플랫폼 - Backend

> OSS 프로젝트 주차 문제 해결 플랫폼 PlinkU의 백엔드 레포지토리입니다.
---

## 📘 프로젝트 개요

이 레포지토리는 OSS 2025-2 수업의 **주차 문제 해결 플랫폼 백엔드**을 위한 저장소입니다.
주요 기능은 다음과 같습니다.

* 사용자 회원가입 및 로그인
* 주차장 안내
* 전기차 충전소 안내
* 주차장 마켓 플레이스

---

## ⚙️ 기술 스택

| 분류        | 기술                                |
| :-------- | :-------------------------------- |
| Language  | Python 3.12                       |
| Framework | Flask                             |
| Database  | SQLite |
| ORM       | SQLAlchemy                        |
| Auth      | JWT                               |
| API       | RESTful 구조                        |

---

## 📂 프로젝트 구조

```
/BE

```

---

## 🚀 실행 방법

### 1️⃣ 가상환경 생성 및 활성화

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2️⃣ 의존성 설치

```bash
pip install -r requirements.txt
```

### 3️⃣ 서버 실행

```bash
python run.py
```

### 4️⃣ 기본 접속 주소

```
http://localhost:5000
```

---

## 🧾 커밋 컨벤션

### 1. 형식

```
type: subject
body
footer
```

---

### 2. Commit Type

| 타입           | 설명                      |
| :----------- | :---------------------- |
| **feat**     | 새로운 기능 추가               |
| **fix**      | 버그 수정                   |
| **docs**     | 문서 수정                   |
| **style**    | 코드 포맷 변경 (세미콜론, 들여쓰기 등) |
| **refactor** | 코드 리팩토링                 |
| **test**     | 테스트 코드 추가 및 수정          |
| **chore**    | 빌드 업무, 패키지 매니저 수정 등     |

---

### 3. Subject 작성 규칙

* 제목은 **50자 이하**, 마침표나 특수기호 사용 ❌
* 영어는 **동사 원형 + 대문자 시작** (ex. `Add`, `Fix`, `Modify`)
* **개조식 구문**으로 작성

**예시**

```
Fixed → Fix
Added → Add
Modified → Modify
```

---

### 4. Body 작성 규칙

* 변경 사항을 **무엇을 / 왜** 변경했는지 중심으로 작성
* 분량 제한 없음 (최대한 구체적으로 작성)

---

### 5. Footer (Option)

* 이슈 트래커 ID를 명시
* 형식: `유형: #이슈번호`
* 여러 개 작성 시 쉼표(,)로 구분

| 유형              | 설명           |
| :-------------- | :----------- |
| **Fixes:**      | 이슈 수정 중      |
| **Resolves:**   | 이슈 해결 완료     |
| **Ref:**        | 참고용 이슈       |
| **Related to:** | 관련된 이슈 (미해결) |

**예시**

```
Feat: "회원 가입 기능 구현"

SMS, 이메일 중복확인 API 개발

Resolves: #123
Ref: #456
Related to: #48, #45
```

---

## 🌿 브랜치 전략

| 브랜치               | 용도        |
| :---------------- | :-------- |
| **main**          | 배포용 안정 버전 |
| **develop**       | 통합 개발 브랜치 |
| **feature/***기능명* | 기능 단위 개발  |
| **fix/***이슈명*     | 버그 수정용    |

---

## 👥 기여자

| 이름  | 역할              |
| :-- | :-------------- |
| 김성민 | 백엔드 개발          |
| 임민우 | 백엔드 개발  |
| 정용성 | 백엔드 개발 |

---

## 📚 추가 문서

* API 명세서: [`/docs/api.md`](./docs/api.md)
* ERD 다이어그램: [`/diagrams/erd.png`](./diagrams/erd.png)
