# 구성요소 설명

## 디렉토리 구조

```
twelvelabs-test/
├── .env                    # API Key, Index ID (로컬 전용, git 제외)
├── .github/
│   └── workflows/
│       └── test.yml        # GitHub Actions CI 설정
├── utils/
│   ├── client.py           # SDK 클라이언트 생성 모듈
│   └── config.py           # 환경변수 로드 모듈
├── tests/
│   ├── conftest.py         # pytest fixtures (client, index_id)
│   └── test_search.py      # 전체 테스트 스위트 (39개 케이스)
├── requirements.txt        # 의존성 목록
└── README.md               # 프로젝트 설명
```

---

## 모듈별 역할

### `utils/client.py`

```python
def get_client() -> TwelveLabs
```

- `.env`에서 `TWELVELABS_API_KEY`를 읽어 SDK 클라이언트를 생성해 반환
- API Key가 없으면 `ValueError`를 발생시켜 테스트 전체를 조기 차단
- 클라이언트 생성 로직을 한 곳에서 관리 → 키 교체 시 이 파일만 수정

---

### `utils/config.py`

```python
INDEX_ID: str
```

- `.env`에서 `TWELVELABS_INDEX_ID`를 읽어 모듈 수준 상수로 노출
- Index ID가 없으면 **import 시점**에 `ValueError` 발생
- 테스트 대상 인덱스를 단일 지점에서 제어

---

### `tests/conftest.py`

```python
@pytest.fixture(scope="session")
def client() -> TwelveLabs

@pytest.fixture(scope="session")
def index_id() -> str
```

- `scope="session"`: 테스트 세션 전체에서 클라이언트와 Index ID를 한 번만 생성
- 모든 테스트 함수가 `client`, `index_id`를 파라미터로 선언하면 pytest가 자동 주입
- 실제 API 호출 비용(인증 오버헤드)을 최소화

---

### `tests/test_search.py` — 헬퍼

```python
def _basic_search(client, index_id, query_text="a person walking", **kwargs)
```

| 항목 | 내용 |
|---|---|
| 역할 | `client.search.create()`의 최소 유효 호출을 캡슐화 |
| 고정값 | `search_options=["visual"]`, `query_text="a person walking"` |
| 확장성 | `**kwargs`로 `page_limit`, `group_by` 등 추가 파라미터 전달 가능 |
| 사용 이유 | 반복되는 보일러플레이트 제거, 기본값 변경 시 한 곳만 수정 |

---

### `tests/test_search.py` — 테스트 클래스 목록

| 클래스 | ID 범위 | 케이스 수 | 핵심 검증 대상 |
|---|---|---|---|
| `TestSuccessfulSearch` | SS-01 ~ SS-13 | 13 | 응답 타입, 필드 구조, group_by, operator, user_metadata |
| `TestPagination` | PA-01 ~ PA-06 | 6 | page_limit 경계, next_page_token, 토큰으로 다음 페이지 조회 |
| `TestTranscriptionOptions` | TR-01 ~ TR-03 | 3 | lexical / semantic / 혼합 |
| `TestFiltering` | FI-01 ~ FI-03 | 3 | duration 범위 필터, 존재하지 않는 ID 필터, 실제 ID 필터 |
| `TestEdgeCases` | EC-01 ~ EC-05 | 5 | 결과 없는 쿼리, 긴 쿼리, 전체 옵션 조합, rank 순서 |
| `TestErrorHandling` | EH-01 ~ EH-07 | 7 | 잘못된 index/key/파라미터 → 정확한 HTTP 상태코드 검증 |
| `TestParameterInteraction` | PI-01 | 1 | transcription_options와 search_options 비호환 조합 |
| **합계** | | **39** | |

---

## 사용된 외부 타입 / 예외 클래스

| 타입 / 예외 | 출처 | 설명 |
|---|---|---|
| `TwelveLabs` | `twelvelabs` | SDK 진입점 클라이언트 |
| `SearchResults` | `twelvelabs.types` | `search.create()` 반환 타입 |
| `SearchItem` | `twelvelabs.types` | 결과 목록의 개별 항목 |
| `ApiError` | `twelvelabs.core.api_error` | 모든 API 오류의 기반 클래스 |
| `BadRequestError` | `twelvelabs.errors` | HTTP 400 전용 예외 클래스 |

---

## GitHub Actions CI 구성 요약

```
트리거: push / pull_request → main 브랜치
        schedule: 매일 UTC 00:00 (KST 09:00)

실행 환경: ubuntu-latest, Python 3.11

주요 단계:
  1. 코드 체크아웃
  2. Python 설치 + 의존성 설치
  3. .env 파일 생성 (GitHub Secrets → 환경변수)
  4. pytest 실행
  5. 결과 GitHub Pages에 HTML 리포트로 배포
```