# 테스트 케이스 목록

TwelveLabs SDK의 `search.create()` 메서드를 대상으로 작성된 통합 테스트 전체 목록입니다.  
모든 테스트는 실제 API를 호출하며, 유효한 `.env` 설정이 필요합니다.

---

## 기본 테스트 (`test_search_basic.py`)

| 테스트명 | 설명 |
|---|---|
| `test_search_basic` | `search_options=["visual"]`, `query_text="a person walking"` 으로 기본 검색 호출 후 응답이 `None`이 아닌지 확인 |

---

## Category 1: 정상 동작 (`TestSuccessfulSearch`)

| 테스트명 | 설명 |
|---|---|
| `test_returns_search_results_type` | 반환값이 `SearchResults` 타입인지 확인 |
| `test_text_search_visual` | `search_options=["visual"]` 텍스트 검색 시 `data` 리스트 반환 확인 |
| `test_text_search_transcription` | `search_options=["transcription"]` 검색 정상 동작 확인 |
| `test_text_search_audio` | `search_options=["audio"]` 검색 정상 동작 확인 |
| `test_response_contains_page_info` | `page_info` 필드가 존재하고, `total_results`가 정수인지 확인 |
| `test_search_item_structure_clip_mode` | clip 모드 결과 항목에 `video_id`, `start`, `end`, `rank` 필드가 있는지 확인. `start >= 0`, `end > start` 검증 |
| `test_group_by_clip_is_default` | `group_by` 미지정 시 각 항목에 `clips` 필드가 없는지 확인 (기본값 = clip) |
| `test_group_by_video_returns_grouped_items` | `group_by="video"` 시 항목에 `id`와 `clips` 리스트가 있는지 확인 |
| `test_group_by_clip_explicit` | `group_by="clip"` 명시적 지정 시 정상 동작 확인 |
| `test_operator_or` | `operator="or"`, 복수 search_options 사용 시 정상 동작 확인 |
| `test_operator_and` | `operator="and"`, 복수 search_options 사용 시 정상 동작 확인 |
| `test_include_user_metadata_true` | `include_user_metadata=True` 설정 시 에러 없이 결과 반환 확인 |
| `test_include_user_metadata_false` | `include_user_metadata=False` 설정 시 에러 없이 결과 반환 확인 |

---

## Category 2: 페이지네이션 (`TestPagination`)

| 테스트명 | 설명 |
|---|---|
| `test_page_limit_one` | `page_limit=1` 시 결과가 1개 이하인지 확인 |
| `test_page_limit_max` | `page_limit=50` (최대값) 시 결과가 50개 이하인지 확인 |
| `test_page_info_limit_per_page_matches_request` | `page_info.limit_per_page` 값이 요청한 `page_limit`과 일치하는지 확인 |
| `test_next_page_token_present_when_more_results` | 전체 결과가 1페이지를 초과할 때 `next_page_token`이 존재하는지 확인 |
| `test_retrieve_next_page_via_token` | `next_page_token`을 `search.retrieve()`에 전달해 다음 페이지를 정상 조회하는지 확인. 1페이지만 있는 경우 skip |
| `test_retrieve_expired_token_raises_error` | 잘못된 토큰으로 `search.retrieve()` 호출 시 `ApiError` (400 또는 404) 발생 확인 |

---

## Category 3: Transcription 옵션 (`TestTranscriptionOptions`)

| 테스트명 | 설명 |
|---|---|
| `test_transcription_lexical_only` | `transcription_options=["lexical"]` — 정확한 단어 매칭 모드 정상 동작 확인 |
| `test_transcription_semantic_only` | `transcription_options=["semantic"]` — 의미 기반 매칭 모드 정상 동작 확인 |
| `test_transcription_both_options` | `transcription_options=["lexical", "semantic"]` — 두 옵션 동시 사용 시 정상 동작 확인 (API 기본값) |

---

## Category 4: 필터링 (`TestFiltering`)

| 테스트명 | 설명 |
|---|---|
| `test_filter_by_duration_range` | `{"duration": {"gte": 1, "lte": 99999}}` 필터 JSON 문자열 정상 수신 확인 |
| `test_filter_by_nonexistent_video_id_raises_bad_request` | 인덱스에 없는 video ID로 필터링 시 `BadRequestError` (400, `search_video_not_in_same_index`) 발생 확인. *예상과 달리 빈 결과가 아닌 에러를 반환하는 실제 API 동작 반영* |
| `test_filter_by_video_id_from_results` | 직전 검색 결과에서 추출한 video ID로 필터링 시, 반환된 모든 항목의 `video_id`가 해당 ID와 일치하는지 확인 |

---

## Category 5: 엣지 케이스 (`TestEdgeCases`)

| 테스트명 | 설명 |
|---|---|
| `test_query_with_no_likely_match_returns_empty` | 매칭 가능성이 극히 낮은 쿼리(`zzz_highly_unlikely_query_xyz_12345`) 요청 시 에러 없이 결과 반환 확인 |
| `test_long_query_text_within_limit` | 약 150 토큰 길이의 쿼리(500 토큰 제한 이내) 정상 처리 확인 |
| `test_all_three_search_options_with_or` | `visual`, `audio`, `transcription` 세 옵션 동시 사용 + `operator="or"` 시 에러 없이 결과 반환 확인 |
| `test_page_limit_one_returns_at_most_one_item` | `page_limit=1` 시 결과가 정확히 0개 또는 1개인지 확인 |
| `test_result_ranks_are_sequential` | 반환된 결과의 `rank` 값이 오름차순 정렬되어 있는지 확인. 결과가 2개 미만이면 skip |

---

## Category 6: 에러 핸들링 (`TestErrorHandling`)

| 테스트명 | 설명 |
|---|---|
| `test_nonexistent_index_id_raises_api_error` | 존재하지 않는 `index_id` 사용 시 `ApiError` (404) 발생 확인 |
| `test_invalid_api_key_raises_api_error` | 잘못된 API 키 사용 시 `ApiError` (401 또는 403) 발생 확인 |
| `test_page_limit_exceeds_maximum_raises_bad_request` | `page_limit=51` (최대값 50 초과) 시 `BadRequestError` (400) 발생 확인 |
| `test_invalid_filter_syntax_raises_bad_request` | 유효하지 않은 JSON 형식의 `filter` 문자열 전달 시 `BadRequestError` (400) 발생 확인 |
| `test_empty_search_options_raises_bad_request` | `search_options=[]` (빈 리스트) 전달 시 400 에러 발생 확인 |
| `test_unsupported_search_option_raises_bad_request` | `search_options=["invalid_option"]` 전달 시 400 에러 발생 확인 |

---

## 요약

| 카테고리 | 케이스 수 |
|---|---|
| 기본 테스트 | 1 |
| 정상 동작 | 13 |
| 페이지네이션 | 6 |
| Transcription 옵션 | 3 |
| 필터링 | 3 |
| 엣지 케이스 | 5 |
| 에러 핸들링 | 6 |
| **합계** | **37** |

> **참고:** 일부 테스트는 인덱스에 충분한 영상 데이터가 없을 경우 `pytest.skip()`으로 건너뜁니다.