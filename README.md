# TwelveLabs SDK – Search Test Suite

Automated integration tests for the `search.create()` method of the [TwelveLabs Python SDK](https://github.com/twelvelabs-io/twelvelabs-python).

---

## Setup

### 1. Prerequisites

- Python 3.9+
- A TwelveLabs account with an API key
- An index that already contains at least one uploaded and indexed video

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure credentials

Copy the `.env` file template and fill in your values:

```
TWELVELABS_API_KEY=<your API key from the Playground>
TWELVELABS_INDEX_ID=<the index ID containing your uploaded video>
```

> **Note:** All tests that make real search calls require a valid API key and an index ID that belongs to your account. You can obtain both from the [TwelveLabs Playground](https://playground.twelvelabs.io/).

---

## Running the Tests

Run the full suite:

```bash
pytest
```

Run only the comprehensive search tests:

```bash
pytest tests/test_search.py -v
```

Run a single test:

```bash
pytest tests/test_search.py::TestErrorHandling::test_invalid_api_key_raises_api_error -v
```

---

## Testing Approach

All tests are **integration tests** — they call the real TwelveLabs API. There are no mocks. This decision was made to validate actual SDK behavior end-to-end, as the assignment explicitly asks to "focus on testing the SDK's functionality rather than direct API calls."

### Test Categories

| ID | Category | Class | What it covers |
|---|---|---|---|
| SS-01 ~ SS-13 | Successful operations | `TestSuccessfulSearch` | Text search with visual / audio / transcription options, grouping by clip vs video, `or`/`and` operators, user metadata |
| PA-01 ~ PA-06 | Pagination | `TestPagination` | `page_limit` bounds, `page_info` fields, `next_page_token`, `search.retrieve()` |
| TR-01 ~ TR-03 | Transcription options | `TestTranscriptionOptions` | `lexical`, `semantic`, and both combined |
| FI-01 ~ FI-03 | Filtering | `TestFiltering` | Duration range filter, filter by video ID, filter that produces empty results |
| EC-01 ~ EC-05 | Edge cases | `TestEdgeCases` | Unlikely query, long query text (~150 tokens), all three search options together, rank ordering |
| EH-01 ~ EH-06 | Error handling | `TestErrorHandling` | Non-existent index (404), invalid API key (401/403), `page_limit > 50` (400), malformed filter JSON (400), empty `search_options` (400), unsupported search option value (400) |

### Parameters Tested

| Parameter | Values / scenarios |
|---|---|
| `search_options` | `visual`, `audio`, `transcription`, all three, empty list, invalid value |
| `query_text` | Normal, long (~150 tokens), unlikely match |
| `group_by` | `clip` (default), `video` |
| `operator` | `or`, `and` |
| `page_limit` | `1`, `5`, `50` (max), `51` (over max) |
| `transcription_options` | `lexical`, `semantic`, both |
| `filter` | Duration range, ID list, malformed JSON |
| `include_user_metadata` | `True`, `False` |

Parameters not tested: `query_media_url`, `query_media_file`, `query_media_type` (image queries). These require publicly accessible image URLs and were out of scope for this assignment.

### Key Assumptions

- The index already has at least one video indexed before running tests. Creating indexes and uploading videos is explicitly out of scope per the assignment.
- Test method: `client.search.create()`. The SDK documentation refers to a `query()` method, but the installed SDK (`twelvelabs==1.2.2`) exposes `create()` on the search client. The return type is `SearchResults` (not `SyncPager[SearchItem]` as the docs describe), with `data`, `page_info`, and `search_pool` fields.
- Error tests that use the `index_id` fixture (e.g., `test_unsupported_search_option_raises_bad_request`) require valid credentials to run correctly, since the API validates authorization before parameter values.

---

## SDK Version

```
twelvelabs==1.2.2
```