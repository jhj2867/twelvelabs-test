# TwelveLabs SDK – 검색 테스트 스위트

[TwelveLabs Python SDK](https://github.com/twelvelabs-io/twelvelabs-python)의 `search.create()` 메서드에 대한 자동화 통합 테스트입니다.

**[📄 테스트 문서 보기 (GitHub Pages)](https://jhj2867.github.io/twelvelabs-test/)** — 접근 방식, 테스트 범위, SDK 버전 등 확인 가능

**[📊 Allure Trend 리포트](https://jhj2867.github.io/twelvelabs-test/allure/)** — 매 실행마다 누적되는 테스트 결과 및 추이 차트 확인 가능

> GitHub Actions가 **매일 한국 시간 오전 9시(UTC 00:00)에 자동으로 전체 테스트를 실행**합니다. `main` 브랜치 push 및 PR 시에도 자동 실행됩니다. Allure 리포트에서 날짜별 추이를 확인할 수 있습니다.

---

## 사전 요구사항

- Python 3.9 이상
- TwelveLabs 계정 및 API 키
- 영상이 최소 1개 이상 업로드·인덱싱된 인덱스

---

## 설치 및 설정

### 1. 레포지토리 클론

```bash
git clone https://github.com/jhj2867/twelvelabs-test.git
cd twelvelabs-test
```

### 2. 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. TwelveLabs SDK 및 의존성 설치

```bash
pip install -r requirements.txt
```

`requirements.txt`에는 TwelveLabs Python SDK(`twelvelabs==1.2.2`)와 pytest 등 필요한 패키지가 모두 포함되어 있습니다.

SDK만 단독으로 설치하려면:

```bash
pip install twelvelabs
```

### 4. 인증 정보 설정

> [!IMPORTANT]
> **이 단계를 완료하지 않으면 테스트가 정상적으로 실행되지 않습니다.**
> 모든 테스트는 실제 TwelveLabs API를 호출하며, 유효한 API 키와 인덱스 ID가 없으면 즉시 오류가 발생합니다.

프로젝트 루트에 `.env` 파일을 생성하고 아래 값을 입력합니다:

```
TWELVELABS_API_KEY=<API 키>
TWELVELABS_INDEX_ID=<인덱스 ID>
```

API 키와 인덱스 ID는 [TwelveLabs Playground](https://playground.twelvelabs.io/)에서 확인할 수 있습니다.

추가로, 인덱스에 **영상이 최소 1개 이상 업로드·인덱싱되어 있어야** 정상 동작 테스트가 실행됩니다.

---

## 테스트 실행

전체 테스트 실행:

```bash
pytest
```

상세 출력과 함께 실행:

```bash
pytest -v
```

카테고리별 실행:

```bash
pytest tests/test_search.py::TestSuccessfulSearch -v
pytest tests/test_search.py::TestPagination -v
pytest tests/test_search.py::TestErrorHandling -v
```

단일 테스트 실행:

```bash
pytest tests/test_search.py::TestSuccessfulSearch::test_SS01_returns_search_results_type -v
```

---

## 테스트 구성

### 카테고리

| ID | 카테고리 | 클래스 | 개수 | 테스트 내용 |
|---|---|---|---|---|
| SS-01 ~ SS-13 | 정상 동작 | `TestSuccessfulSearch` | 13 | visual·audio·transcription 검색, clip·video 그룹핑, `or`/`and` 연산자, 사용자 메타데이터 |
| PA-01 ~ PA-06 | 페이지네이션 | `TestPagination` | 6 | `page_limit` 경계값, `page_info` 필드, `next_page_token`, `search.retrieve()` |
| TR-01 ~ TR-03 | 트랜스크립션 옵션 | `TestTranscriptionOptions` | 3 | `lexical`, `semantic`, 둘 다 사용 |
| FI-01 ~ FI-03 | 필터링 | `TestFiltering` | 3 | 재생 시간 범위 필터, 영상 ID 필터, 잘못된 ID 필터 |
| EC-01 ~ EC-05 | 엣지 케이스 | `TestEdgeCases` | 5 | 검색 결과 없는 쿼리, 긴 쿼리 텍스트(~150 토큰), 세 가지 옵션 동시 사용, 순위 정렬 |
| EH-01 ~ EH-08 | 에러 처리 | `TestErrorHandling` | 8 | 존재하지 않는 인덱스(404), 잘못된 API 키(401/403), `page_limit > 50`(400), 잘못된 필터 JSON(400), 빈 `search_options`(400), 지원하지 않는 검색 옵션(400), 빈 `query_text`(400), `page_limit=0`(400) |
| PI-01 | 파라미터 상호작용 | `TestParameterInteraction` | 1 | `transcription_options`과 non-transcription `search_options` 동시 사용 |

**총 39개 테스트**

### 테스트 대상 파라미터

| 파라미터 | 테스트 값 / 시나리오 |
|---|---|
| `search_options` | `visual`, `audio`, `transcription`, 세 가지 모두, 빈 리스트, 잘못된 값 |
| `query_text` | 일반, 긴 텍스트(~150 토큰), 결과 없는 쿼리 |
| `group_by` | `clip`(기본값), `video` |
| `operator` | `or`, `and` |
| `page_limit` | `1`, `5`, `50`(최대), `51`(초과) |
| `transcription_options` | `lexical`, `semantic`, 둘 다 |
| `filter` | 재생 시간 범위, ID 리스트, 잘못된 JSON |
| `include_user_metadata` | `True`, `False` |

미테스트 파라미터: `query_media_url`, `query_media_file`, `query_media_type` (이미지 쿼리). 공개 접근 가능한 이미지 URL이 필요하여 이번 범위에서 제외했습니다. `sort_option`은 공식 문서(1.3)에 언급되어 있으나 실제 SDK 1.2.2에 존재하지 않아 제외했습니다.

---

## 테스트 방식

모든 테스트는 **통합 테스트**로, 실제 TwelveLabs API를 호출합니다. 목(mock)은 사용하지 않습니다. SDK의 실제 동작을 엔드투엔드로 검증하기 위한 의도적인 선택입니다.

### 주요 전제사항

- 테스트 실행 전 인덱스에 최소 1개의 영상이 인덱싱되어 있어야 합니다. 인덱스 생성 및 영상 업로드는 테스트 범위에서 제외했습니다.
- 호출 메서드: `client.search.create()`. SDK 문서에는 `query()` 메서드가 언급되어 있으나, 설치된 SDK(`twelvelabs==1.2.2`)에서는 `create()`를 사용합니다. 반환 타입은 문서상의 `SyncPager[SearchItem]`이 아닌 `SearchResults`이며, `data`, `page_info`, `search_pool` 필드를 포함합니다.
- 에러 처리 테스트 중 `index_id` 픽스처를 사용하는 테스트(예: `test_EH06`)는 API가 파라미터 유효성 검사 전에 인증을 먼저 확인하므로 유효한 인증 정보가 필요합니다.

---

## SDK 버전

```
twelvelabs==1.2.2
```

> **참고:** [공식 문서](https://docs.twelvelabs.io/sdk-reference/python/search)는 `1.3` 기준으로 작성되어 있으나, PyPI 최신 배포 버전은 `1.2.2`입니다. 테스트는 실제 설치 가능한 `1.2.2` 기준으로 작성했습니다.

### 1.2.2 vs 문서(1.3) 주요 차이점

| 항목 | 문서 (1.3) | 실제 SDK (1.2.2) |
|---|---|---|
| 메서드명 | `client.search.query()` | `client.search.create()` |
| 반환 타입 | `SyncPager[SearchItem]` | `SearchResults` |
| 페이지 이동 | `pager.has_next` / `pager.next_page()` | `page_info.next_page_token` + `search.retrieve()` |
| 복수 이미지 쿼리 | `query_media_urls`, `query_media_files` 지원 | 미지원 |
| `sort_option` | 문서에 명시 | 미지원 (파라미터 없음) |
| `transcription_options` | 문서 미명시 | 지원 (`lexical`, `semantic`) |
| `include_user_metadata` | 문서 미명시 | 지원 |