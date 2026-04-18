# 테스트 케이스 설계 메뉴얼

> 이 문서는 "왜 이 테스트를 만들었는가"를 기준으로 각 케이스의 의도를 설명합니다.

---

## 설계 원칙

TwelveLabs SDK의 `search.create()`는 파라미터가 많고, 실패 조건이 다양합니다.  
테스트 스위트는 다음 세 가지 질문에 답하도록 설계되었습니다.

1. **"정상 동작하는가?"** — 유효한 파라미터 조합에서 올바른 응답 구조를 반환하는지
2. **"경계에서 버티는가?"** — page_limit 최대치, 긴 쿼리, 결과 없는 쿼리 등에서 안정적인지
3. **"잘못된 입력을 정확히 거부하는가?"** — 잘못된 파라미터에 대해 예상한 HTTP 상태코드로 실패하는지

---

## 카테고리별 설계 의도

---

### SS (Successful Search) — 성공 케이스 · 13개

SDK의 핵심 기능이 정상 작동하는지 확인하는 가장 기본적인 검증 그룹입니다.

| ID | 테스트명 | 설계 의도 |
|---|---|---|
| SS-01 | returns_search_results_type | 반환값이 `SearchResults` 타입인지 타입 자체를 검증. SDK 버전 변경 시 첫 번째로 깨질 케이스 |
| SS-02 | text_search_visual | visual 옵션 + 텍스트 쿼리가 가장 기본 조합. `data`가 list인지 확인 |
| SS-03 | text_search_transcription | `search_options=["transcription"]`이 독립적으로 동작하는지 확인 |
| SS-04 | text_search_audio | `search_options=["audio"]`가 독립적으로 동작하는지 확인 |
| SS-05 | response_contains_page_info | `page_info.total_results`가 정수형으로 존재하는지 — 페이지네이션의 전제조건 |
| SS-06 | search_item_structure_clip_mode | 개별 `SearchItem`에 `video_id`, `start`, `end`, `rank`가 있고 `end > start`인지 |
| SS-07 | group_by_clip_is_default | `group_by` 미지정 시 기본값이 clip이고 `clips` 필드가 없는지 |
| SS-08 | group_by_video_returns_grouped_items | `group_by="video"` 시 `id`와 `clips` 리스트가 중첩 구조로 오는지 |
| SS-09 | group_by_clip_explicit | `group_by="clip"` 명시 시에도 동일하게 동작하는지 |
| SS-10 | operator_or | `visual + transcription + operator="or"` 조합이 결과를 넓히는 방향으로 허용되는지 |
| SS-11 | operator_and | `visual + transcription + operator="and"` 조합이 좁히는 방향으로 허용되는지 |
| SS-12 | include_user_metadata_true | 메타데이터 포함 요청이 오류 없이 처리되는지 |
| SS-13 | include_user_metadata_false | 메타데이터 미포함 요청이 오류 없이 처리되는지 |

---

### PA (Pagination) — 페이지네이션 · 6개

결과가 많을 때 분할 조회가 올바르게 동작하는지 검증합니다.

| ID | 테스트명 | 설계 의도 |
|---|---|---|
| PA-01 | page_limit_one | 최솟값 1이 실제로 최대 1개만 반환하는지 |
| PA-02 | page_limit_max | 최댓값 50이 50개를 초과하지 않는지 |
| PA-03 | page_info_limit_per_page_matches_request | 요청한 `page_limit`이 응답의 `limit_per_page`에 그대로 반영되는지 |
| PA-04 | next_page_token_present_when_more_results | 결과가 더 있을 때 `next_page_token`이 채워지는지 |
| PA-05 | retrieve_next_page_via_token | 토큰으로 `search.retrieve()`를 호출해 실제로 다음 페이지를 가져오는지 |
| PA-06 | retrieve_expired_token_raises_error | 유효하지 않은 토큰에 대해 400/404로 실패하는지 |

---

### TR (Transcription Options) — 트랜스크립션 옵션 · 3개

음성 인식 방식(정확 일치 vs 의미 기반)의 옵션 조합을 검증합니다.

| ID | 테스트명 | 설계 의도 |
|---|---|---|
| TR-01 | transcription_lexical_only | `lexical`만 지정해도 동작하는지 |
| TR-02 | transcription_semantic_only | `semantic`만 지정해도 동작하는지 |
| TR-03 | transcription_both_options | 둘 다 지정하는 기본값 동작을 명시적으로 검증 |

---

### FI (Filtering) — 필터링 · 3개

검색 결과를 좁히는 필터 기능을 검증합니다.

| ID | 테스트명 | 설계 의도 |
|---|---|---|
| FI-01 | filter_by_duration_range | 유효한 JSON 필터 문자열이 정상 처리되는지 (`{"duration": {"gte": 1, "lte": 99999}}`) |
| FI-02 | filter_by_nonexistent_video_id_raises_bad_request | 인덱스에 없는 video ID 필터 시 `search_video_not_in_same_index` 에러코드로 400이 오는지 |
| FI-03 | filter_by_video_id_from_results | 실제 검색 결과에서 뽑은 video ID로 필터링하면 해당 비디오만 돌아오는지 |

> FI-03은 두 번의 API 호출을 연결하는 **연계 테스트**입니다. 1차 검색 결과를 입력값으로 활용합니다.

---

### EC (Edge Cases) — 엣지 케이스 · 5개

일반 사용에서 발생할 수 있는 비정상적이거나 경계에 있는 입력을 검증합니다.

| ID | 테스트명 | 설계 의도 |
|---|---|---|
| EC-01 | query_with_no_likely_match_returns_empty | 결과 0건일 때 예외 없이 빈 list를 반환하는지 (오류와 구분) |
| EC-02 | long_query_text_within_limit | 500 토큰 미만의 긴 쿼리가 오류 없이 처리되는지 |
| EC-03 | all_three_search_options_with_or | visual + audio + transcription 전부 + or 조합이 허용되는지 |
| EC-04 | page_limit_one_returns_at_most_one_item | PA-01과 관점이 다름 — 반환값이 0 또는 1이어야 함을 명시 |
| EC-05 | result_ranks_are_sequential | `rank` 필드가 오름차순 정렬되어 오는지 — SDK 문서 명세 준수 여부 |

---

### EH (Error Handling) — 에러 핸들링 · 7개

잘못된 입력에 대해 SDK가 적절한 예외를 발생시키는지, 그리고 HTTP 상태코드가 정확한지 검증합니다.

| ID | 테스트명 | 기대 에러 | 설계 의도 |
|---|---|---|---|
| EH-01 | nonexistent_index_id | 404 ApiError | 존재하지 않는 인덱스 |
| EH-02 | invalid_api_key | 401/403 ApiError | 인증 실패 — 별도 `bad_client` 인스턴스 사용 |
| EH-03 | page_limit_exceeds_maximum | 400 BadRequestError | 최대값(50) 초과 — 경계 +1 테스트 |
| EH-04 | invalid_filter_syntax | 400 BadRequestError | JSON이 아닌 문자열을 filter에 전달 |
| EH-05 | empty_search_options | 400 BadRequestError | `search_options=[]` 빈 리스트 |
| EH-06 | unsupported_search_option | 400 BadRequestError | 지원하지 않는 문자열 값 |
| EH-07 | empty_query_text | 400 BadRequestError | `query_text=""` 빈 문자열 |

---

### PI (Parameter Interaction) — 파라미터 조합 · 1개

| ID | 테스트명 | 설계 의도 |
|---|---|---|
| PI-01 | transcription_options_with_non_transcription_search | `transcription_options`는 `search_options`에 `"transcription"`이 포함될 때만 유효. 없는 상태에서 전달하면 400이어야 함 — 파라미터 간 의존 관계 검증 |

---

## 쿼리 텍스트 설계에 대하여

현재 대부분의 테스트에서 `"a person walking"`이라는 단일 쿼리를 사용합니다.

**이렇게 설계한 이유:**

- 이 테스트 스위트의 목적은 **SDK의 파라미터 처리 동작**을 검증하는 것이지, 검색 결과의 품질(relevance)을 평가하는 것이 아닙니다.
- 쿼리 내용이 다양할수록 "결과가 없는 것이 쿼리 때문인지, SDK 오류 때문인지" 구분이 어려워집니다.
- 하나의 기준 쿼리를 고정하면 파라미터 변경에 따른 동작 차이를 비교하기 쉽습니다.

**다양화가 의미 있는 경우 (향후 확장 방향):**

| 확장 영역 | 예시 |
|---|---|
| 쿼리 언어 | 한국어, 일본어 등 다국어 쿼리 테스트 |
| 특수문자 포함 | `"hello & world"`, 이모지, 긴 URL |
| 시맨틱 유사도 | 동의어 쿼리 결과 일치율 비교 |
| 이미지 쿼리 | `query_media_url`을 사용한 이미지 기반 검색 |

---

## 테스트 격리 전략

```
scope="session"  →  클라이언트 1회 생성, 전체 세션 재사용
pytest.skip()    →  데이터 부재로 검증 불가한 케이스는 실패 대신 skip
pytest.raises()  →  에러 케이스는 반드시 예외 타입 + 상태코드 동시 검증
```

실제 API를 호출하는 통합 테스트이므로, 테스트 간 상태 공유는 최소화하되 인증 오버헤드는 session scope로 한 번만 처리합니다.