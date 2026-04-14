---
layout: default
title: TwelveLabs SDK 검색 테스트 스위트
---

# TwelveLabs SDK 검색 테스트 스위트

TwelveLabs Python SDK의 `search.create()` 메서드에 대한 자동화 통합 테스트 문서입니다.

---

## 접근 방식

### 통합 테스트 선택

모든 테스트는 **실제 TwelveLabs API를 직접 호출하는 통합 테스트**입니다. 목(mock)은 사용하지 않았습니다.

이 선택의 이유:
- SDK가 API 요청을 올바르게 직렬화하는지 검증
- API 응답이 SDK 타입(`SearchResults`, `SearchItem` 등)으로 올바르게 역직렬화되는지 검증
- 실제 엔드포인트에서의 에러 응답 코드와 에러 타입 매핑 검증
- SDK 문서와 실제 동작의 차이 발견 (예: `query()` vs `create()`, 반환 타입 등)

### 테스트 구성 방식

테스트는 6개 카테고리로 구분하여 `tests/test_search.py` 단일 파일에 클래스 형태로 구성했습니다.

| ID | 카테고리 | 개수 |
|---|---|---|
| SS-01 ~ SS-13 | 정상 동작 | 13 |
| PA-01 ~ PA-06 | 페이지네이션 | 6 |
| TR-01 ~ TR-03 | 트랜스크립션 옵션 | 3 |
| FI-01 ~ FI-03 | 필터링 | 3 |
| EC-01 ~ EC-05 | 엣지 케이스 | 5 |
| EH-01 ~ EH-06 | 에러 처리 | 6 |

---

## 테스트 범위 결정

### 포함한 것

**`search.create()` 파라미터 전수 테스트**

| 파라미터 | 테스트한 값 |
|---|---|
| `search_options` | `visual`, `audio`, `transcription`, 세 가지 동시, 빈 리스트, 잘못된 값 |
| `query_text` | 일반, 긴 텍스트(~150 토큰), 결과 없는 쿼리 |
| `group_by` | `clip`(기본값), `video` |
| `operator` | `or`, `and` |
| `page_limit` | `1`, `5`, `50`(최대), `51`(초과) |
| `transcription_options` | `lexical`, `semantic`, 둘 다 |
| `filter` | 재생 시간 범위, 영상 ID 리스트, 잘못된 JSON |
| `include_user_metadata` | `True`, `False` |

**에러 응답 검증**

단순히 예외 발생 여부만 확인하는 것이 아니라, `status_code`와 에러 바디의 `code` 필드까지 검증하여 API 계약을 명확히 테스트합니다.

### 제외한 것

- **`query_media_url` / `query_media_file` / `query_media_type`**: 이미지 쿼리 파라미터. 공개 접근 가능한 이미지 URL이 필요하여 이번 범위에서 제외했습니다.
- **인덱스 생성 및 영상 업로드**: 사전 조건으로 간주하고 테스트 범위에서 제외했습니다.
- **`search.list()`**: 이번 과제의 핵심인 `search.create()`에 집중했습니다.

---

## SDK 버전

```
twelvelabs==1.2.2
```

### 문서와 실제 SDK의 차이

SDK 문서(`docs.twelvelabs.io`)와 실제 설치된 SDK 사이에 몇 가지 차이점이 발견되었습니다.

| 항목 | 문서 | 실제 SDK (1.2.2) |
|---|---|---|
| 메서드명 | `client.search.query()` | `client.search.create()` |
| 반환 타입 | `SyncPager[SearchItem]` | `SearchResults` |
| 응답 필드 | 명세 없음 | `data`, `page_info`, `search_pool` |

테스트는 실제 SDK 동작 기준으로 작성했습니다.

---

## 가정 사항

1. **사전 인덱싱된 영상**: 테스트 실행 전 인덱스에 최소 1개의 영상이 업로드·인덱싱되어 있어야 합니다. 데이터가 없으면 정상 동작 테스트가 `pytest.skip()`으로 건너뜁니다.

2. **인증 우선 검증**: TwelveLabs API는 파라미터 유효성 검사 전에 인증을 먼저 수행합니다. 따라서 에러 처리 테스트(EH 카테고리) 중 `index_id`를 사용하는 테스트는 유효한 API 키가 있어야 예상한 400 에러를 받을 수 있습니다.

3. **실시간 API 의존성**: 네트워크 상태나 TwelveLabs 서비스 상태에 따라 테스트 결과가 영향을 받을 수 있습니다.

4. **`search.retrieve()` 토큰 유효기간**: 페이지 토큰은 발급 후 일정 시간이 지나면 만료됩니다. `test_PA06`은 만료된 토큰으로 에러가 발생하는지 검증합니다.

---

## 프로젝트 구조

```
twelvelabs-test/
├── tests/
│   ├── conftest.py        # client, index_id 픽스처
│   └── test_search.py     # 전체 테스트 스위트 (36개)
├── utils/
│   ├── client.py          # TwelveLabs 클라이언트 생성
│   └── config.py          # 환경 변수 로드
├── .github/
│   └── workflows/
│       └── test.yml       # GitHub Actions CI
├── .env                   # 인증 정보 (git 제외)
├── pytest.ini
├── requirements.txt
└── README.md
```

---

[GitHub 레포지토리 바로가기](https://github.com/jhj2867/twelvelabs-test)