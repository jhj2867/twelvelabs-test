# TwelveLabs SDK – Search Test Suite

Automated integration tests for the `search.create()` method of the [TwelveLabs Python SDK](https://github.com/twelvelabs-io/twelvelabs-python).

---

## Prerequisites

- Python 3.9+
- A TwelveLabs account with an API key
- An index that already contains at least one uploaded and indexed video

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/jhj2867/twelvelabs-test.git
cd twelvelabs-test
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install the TwelveLabs SDK and dependencies

```bash
pip install -r requirements.txt
```

This installs the TwelveLabs Python SDK (`twelvelabs==1.2.2`) along with pytest and all required packages.

To install the SDK standalone:

```bash
pip install twelvelabs
```

### 4. Configure credentials

Create a `.env` file in the project root and fill in your values:

```
TWELVELABS_API_KEY=<your API key from the Playground>
TWELVELABS_INDEX_ID=<the index ID containing your uploaded video>
```

You can obtain both from the [TwelveLabs Playground](https://playground.twelvelabs.io/).

> **Note:** All tests make real API calls. There are no mocks. A valid API key and an index with at least one indexed video are required before running the tests.

---

## Running the Tests

Run the full suite:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run a specific category:

```bash
pytest tests/test_search.py::TestSuccessfulSearch -v
pytest tests/test_search.py::TestPagination -v
pytest tests/test_search.py::TestErrorHandling -v
```

Run a single test by ID:

```bash
pytest tests/test_search.py::TestSuccessfulSearch::test_SS01_returns_search_results_type -v
```

---

## Test Structure

### Categories

| ID | Category | Class | Count | What it covers |
|---|---|---|---|---|
| SS-01 ~ SS-13 | Successful operations | `TestSuccessfulSearch` | 13 | Text search with visual / audio / transcription options, grouping by clip vs video, `or`/`and` operators, user metadata |
| PA-01 ~ PA-06 | Pagination | `TestPagination` | 6 | `page_limit` bounds, `page_info` fields, `next_page_token`, `search.retrieve()` |
| TR-01 ~ TR-03 | Transcription options | `TestTranscriptionOptions` | 3 | `lexical`, `semantic`, and both combined |
| FI-01 ~ FI-03 | Filtering | `TestFiltering` | 3 | Duration range filter, filter by video ID, filter that produces empty results |
| EC-01 ~ EC-05 | Edge cases | `TestEdgeCases` | 5 | Unlikely query, long query text (~150 tokens), all three search options together, rank ordering |
| EH-01 ~ EH-06 | Error handling | `TestErrorHandling` | 6 | Non-existent index (404), invalid API key (401/403), `page_limit > 50` (400), malformed filter JSON (400), empty `search_options` (400), unsupported search option value (400) |

**Total: 36 tests**

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

---

## Testing Approach

All tests are **integration tests** — they call the real TwelveLabs API. There are no mocks. This decision was made to validate actual SDK behavior end-to-end, as the assignment explicitly asks to "focus on testing the SDK's functionality rather than direct API calls."

### Key Assumptions

- The index already has at least one video indexed before running tests. Creating indexes and uploading videos is explicitly out of scope per the assignment.
- Test method: `client.search.create()`. The SDK documentation refers to a `query()` method, but the installed SDK (`twelvelabs==1.2.2`) exposes `create()` on the search client. The return type is `SearchResults` (not `SyncPager[SearchItem]` as the docs describe), with `data`, `page_info`, and `search_pool` fields.
- Error tests that use the `index_id` fixture (e.g., `test_EH06_unsupported_search_option_raises_bad_request`) require valid credentials to run correctly, since the API validates authorization before parameter values.

---

## SDK Version

```
twelvelabs==1.2.2
```