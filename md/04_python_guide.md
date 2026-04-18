# 이 프로젝트에서 사용된 Python 개념 설명

> 코드를 읽을 때 막히는 Python 문법과 패턴을 이 프로젝트 코드 기준으로 설명합니다.

---

## 1. 환경변수와 `.env` 파일

```python
# utils/client.py
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TWELVELABS_API_KEY")
```

- `os.getenv("KEY")` — 운영체제 환경변수를 읽습니다. 없으면 `None` 반환
- `load_dotenv()` — `.env` 파일의 내용을 환경변수로 메모리에 로드합니다  
  (`pip install python-dotenv`로 설치하는 외부 라이브러리)
- `.env` 파일은 `KEY=VALUE` 형식으로 작성하며, 코드에 직접 비밀키를 하드코딩하지 않기 위해 사용

---

## 2. 모듈 수준 예외 발생

```python
# utils/config.py
INDEX_ID = os.getenv("TWELVELABS_INDEX_ID")

if not INDEX_ID:
    raise ValueError("INDEX_ID is missing")
```

- `raise ValueError("메시지")` — 직접 예외를 발생시킵니다
- 이 코드는 함수 안이 아니라 **모듈 최상단**에 있습니다  
  → `import utils.config`를 하는 순간 실행되어, 환경변수 없이는 아예 시작이 안 됩니다
- `if not INDEX_ID:` — `None`이나 빈 문자열 `""` 모두 `False`로 처리됩니다

---

## 3. pytest fixtures

```python
# tests/conftest.py
import pytest

@pytest.fixture(scope="session")
def client():
    return get_client()
```

**fixture란?**  
테스트 함수가 필요로 하는 사전 준비 객체를 만들어주는 함수입니다.  
테스트 함수의 파라미터 이름과 fixture 이름이 같으면 pytest가 자동으로 주입합니다.

```python
# 테스트 함수가 client를 파라미터로 선언하면 자동 주입됨
def test_SS01(self, client, index_id):
    result = client.search.create(...)
```

**`scope="session"`이란?**

| scope | 생성 시점 | 재사용 범위 |
|---|---|---|
| `function` (기본값) | 테스트 함수마다 | 해당 함수 1개 |
| `class` | 클래스마다 | 클래스 내 전체 |
| `session` | 테스트 시작 시 1회 | 전체 테스트 세션 |

이 프로젝트는 `scope="session"`을 사용해 API 클라이언트를 한 번만 만들고 전체 39개 테스트에서 재사용합니다.

---

## 4. 클래스로 테스트 묶기

```python
class TestSuccessfulSearch:

    def test_SS01_returns_search_results_type(self, client, index_id):
        ...
```

- pytest는 `Test`로 시작하는 클래스와 `test_`로 시작하는 함수를 자동으로 테스트로 인식합니다
- 클래스로 묶는 이유: 관련 테스트를 그룹화해 가독성을 높이고, `pytest tests/test_search.py::TestSuccessfulSearch`처럼 클래스 단위로 실행 가능
- 클래스 내 메서드는 반드시 첫 번째 파라미터로 `self`를 받습니다

---

## 5. `**kwargs` — 키워드 인수 묶음

```python
def _basic_search(client, index_id, query_text="a person walking", **kwargs):
    return client.search.create(
        index_id=index_id,
        search_options=["visual"],
        query_text=query_text,
        **kwargs,  # 나머지 파라미터를 그대로 전달
    )
```

- `**kwargs`는 "이름 있는 추가 인수를 딕셔너리로 받겠다"는 의미입니다
- 호출 시 `_basic_search(client, index_id, page_limit=5)`처럼 쓰면  
  `kwargs = {"page_limit": 5}`가 되고, `**kwargs`로 펼쳐서 전달됩니다
- 함수 시그니처를 바꾸지 않고도 하위 함수에 임의의 파라미터를 전달할 수 있어 유연합니다

---

## 6. `isinstance()` — 타입 검사

```python
assert isinstance(result, SearchResults)
assert isinstance(result.data, list)
```

- `isinstance(객체, 타입)` — 객체가 해당 타입(또는 그 하위 타입)의 인스턴스인지 `True`/`False`로 반환
- `type(result) == SearchResults`와 달리, 상속 관계도 포함해 검사합니다
- 테스트에서는 SDK가 반환하는 객체의 타입이 문서와 일치하는지 확인하는 용도로 사용

---

## 7. `pytest.raises()` — 예외 검증

```python
with pytest.raises(ApiError) as exc_info:
    client.search.create(
        index_id="000000000000000000000000",
        ...
    )
assert exc_info.value.status_code == 404
```

- `with pytest.raises(예외타입):` — 블록 안에서 해당 예외가 발생해야 테스트 통과
- 예외가 발생하지 않으면 테스트 실패
- `exc_info.value` — 발생한 예외 객체 자체에 접근해 `status_code` 같은 속성을 추가 검증

**여러 예외 타입을 동시에 허용하는 경우:**

```python
with pytest.raises((BadRequestError, ApiError)) as exc_info:
    ...
```

- 튜플로 전달하면 둘 중 하나가 발생해도 통과합니다

---

## 8. `pytest.skip()` — 조건부 건너뛰기

```python
if not result.data:
    pytest.skip("No results returned — cannot verify item structure.")
```

- 데이터가 없으면 검증 자체가 불가능한 경우, 실패(FAIL)가 아닌 건너뜀(SKIP)으로 처리
- 외부 데이터(실제 인덱스 내용)에 의존하는 통합 테스트에서 자주 사용하는 패턴
- CI 리포트에서 SKIP은 빨간색(FAIL)이 아닌 노란색으로 표시됩니다

---

## 9. `assert` — 검증문

```python
assert result.page_info is not None
assert item.end > item.start
assert len(result.data) <= 50
```

- `assert 조건` — 조건이 `False`이면 `AssertionError`를 발생시켜 테스트를 실패시킵니다
- pytest는 실패 시 조건식 양쪽 값을 자동으로 출력해줍니다  
  예: `assert 3 <= 50` → 실패 시 `AssertionError: assert 3 <= 50`

---

## 10. `json.dumps()` — 딕셔너리 → JSON 문자열 변환

```python
import json

duration_filter = json.dumps({"duration": {"gte": 1, "lte": 99999}})
# 결과: '{"duration": {"gte": 1, "lte": 99999}}'
```

- TwelveLabs `filter` 파라미터는 **문자열(str)** 형태의 JSON을 요구합니다
- Python 딕셔너리를 그대로 전달하면 안 되고, `json.dumps()`로 JSON 문자열로 변환해야 합니다
- 반대 방향(`json.loads()`)은 JSON 문자열 → Python 딕셔너리 변환입니다

---

## 11. `conftest.py`의 역할

pytest는 테스트 실행 전에 `conftest.py`를 자동으로 읽습니다.  
별도의 import 없이도 같은 디렉토리(또는 상위 디렉토리)의 `conftest.py`에 정의된 fixture를 모든 테스트에서 사용할 수 있습니다.

```
tests/
├── conftest.py     ← 여기 정의된 client, index_id fixture를
└── test_search.py  ← 여기서 자동으로 사용 가능
```

---

## 12. f-string이 없는 이유

이 프로젝트의 테스트 코드에는 f-string이 등장하지 않습니다.  
테스트에서는 값을 출력하는 것보다 **값을 검증(assert)** 하는 것이 목적이기 때문입니다.  
참고로 f-string 문법은 다음과 같습니다.

```python
name = "TwelveLabs"
print(f"Hello, {name}!")  # → Hello, TwelveLabs!
```

---

## 요약 — 이 프로젝트에서 쓰인 Python 핵심 패턴

| 패턴 | 사용 위치 | 목적 |
|---|---|---|
| `os.getenv` + `load_dotenv` | `utils/` | 환경변수에서 API Key 로드 |
| 모듈 수준 `raise` | `utils/config.py` | 환경변수 없으면 즉시 중단 |
| `@pytest.fixture(scope="session")` | `conftest.py` | 클라이언트 1회 생성 후 재사용 |
| `**kwargs` | `_basic_search` | 헬퍼 함수에 추가 파라미터 전달 |
| `isinstance()` | 각 테스트 | SDK 반환 타입 검증 |
| `pytest.raises()` | EH/FI/PI 테스트 | 예외 발생 + 상태코드 검증 |
| `pytest.skip()` | 데이터 의존 테스트 | 데이터 없을 때 FAIL 대신 SKIP |
| `json.dumps()` | FI 테스트 | 딕셔너리를 filter 문자열로 변환 |