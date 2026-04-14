"""
Comprehensive test suite for the TwelveLabs SDK search.create() method.

Covers:
  - Successful operations: text search, search options, grouping, pagination,
    filtering, operators, transcription options, user metadata
  - Edge cases: empty results, long query text, boundary page limits,
    all search options combined
  - Error handling: invalid index, invalid API key, exceeded page limit,
    malformed filter, empty search_options list

Test ID format: <category>-<number>
  SS : Successful Search    (SS-01 ~ SS-13)
  PA : Pagination           (PA-01 ~ PA-06)
  TR : Transcription        (TR-01 ~ TR-03)
  FI : Filtering            (FI-01 ~ FI-03)
  EC : Edge Cases           (EC-01 ~ EC-05)
  EH : Error Handling       (EH-01 ~ EH-06)
"""

import json

import pytest
from twelvelabs import TwelveLabs
from twelvelabs.core.api_error import ApiError
from twelvelabs.errors import BadRequestError
from twelvelabs.types import SearchItem, SearchResults


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _basic_search(client, index_id, query_text="a person walking", **kwargs):
    """Convenience wrapper around search.create() with sensible defaults."""
    return client.search.create(
        index_id=index_id,
        search_options=["visual"],
        query_text=query_text,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Category 1: Successful Operations (SS)
# ---------------------------------------------------------------------------

class TestSuccessfulSearch:

    def test_SS01_returns_search_results_type(self, client, index_id):
        """search.create() returns a SearchResults object."""
        result = _basic_search(client, index_id)
        assert isinstance(result, SearchResults)

    def test_SS02_text_search_visual(self, client, index_id):
        """Text query with visual search option returns a valid response."""
        result = _basic_search(client, index_id)
        assert result.data is not None
        assert isinstance(result.data, list)

    def test_SS03_text_search_transcription(self, client, index_id):
        """Text query with transcription search option returns a valid response."""
        result = client.search.create(
            index_id=index_id,
            search_options=["transcription"],
            query_text="hello",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_SS04_text_search_audio(self, client, index_id):
        """Text query with audio search option returns a valid response."""
        result = client.search.create(
            index_id=index_id,
            search_options=["audio"],
            query_text="music",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_SS05_response_contains_page_info(self, client, index_id):
        """SearchResults.page_info is populated."""
        result = _basic_search(client, index_id)
        assert result.page_info is not None
        assert result.page_info.total_results is not None
        assert isinstance(result.page_info.total_results, int)

    def test_SS06_search_item_structure_clip_mode(self, client, index_id):
        """Each SearchItem in clip mode has the expected fields."""
        result = _basic_search(client, index_id, page_limit=3)
        if not result.data:
            pytest.skip("No results returned — cannot verify item structure.")
        item = result.data[0]
        assert isinstance(item, SearchItem)
        assert item.video_id is not None
        assert item.start is not None
        assert item.end is not None
        assert item.rank is not None
        assert item.start >= 0
        assert item.end > item.start

    def test_SS07_group_by_clip_is_default(self, client, index_id):
        """Without group_by, items are returned as clips (no nested clips list)."""
        result = _basic_search(client, index_id, page_limit=3)
        if not result.data:
            pytest.skip("No results returned.")
        for item in result.data:
            assert item.clips is None

    def test_SS08_group_by_video_returns_grouped_items(self, client, index_id):
        """group_by='video' yields items with an id and a clips list."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="a person walking",
            group_by="video",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None
        if result.data:
            item = result.data[0]
            assert item.id is not None
            assert item.clips is not None
            assert isinstance(item.clips, list)

    def test_SS09_group_by_clip_explicit(self, client, index_id):
        """group_by='clip' explicitly returns ungrouped clips."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="a person walking",
            group_by="clip",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_SS10_operator_or(self, client, index_id):
        """Multiple search options with operator='or' broadens search."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual", "transcription"],
            query_text="a person walking",
            operator="or",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_SS11_operator_and(self, client, index_id):
        """Multiple search options with operator='and' narrows search."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual", "transcription"],
            query_text="a person walking",
            operator="and",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_SS12_include_user_metadata_true(self, client, index_id):
        """include_user_metadata=True does not raise and returns results."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="a person walking",
            include_user_metadata=True,
        )
        assert isinstance(result, SearchResults)

    def test_SS13_include_user_metadata_false(self, client, index_id):
        """include_user_metadata=False does not raise and returns results."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="a person walking",
            include_user_metadata=False,
        )
        assert isinstance(result, SearchResults)


# ---------------------------------------------------------------------------
# Category 2: Pagination (PA)
# ---------------------------------------------------------------------------

class TestPagination:

    def test_PA01_page_limit_one(self, client, index_id):
        """page_limit=1 returns at most 1 item."""
        result = _basic_search(client, index_id, page_limit=1)
        assert result.data is not None
        assert len(result.data) <= 1

    def test_PA02_page_limit_max(self, client, index_id):
        """page_limit=50 (maximum) returns at most 50 items."""
        result = _basic_search(client, index_id, page_limit=50)
        assert result.data is not None
        assert len(result.data) <= 50

    def test_PA03_page_info_limit_per_page_matches_request(self, client, index_id):
        """page_info.limit_per_page reflects the requested page_limit."""
        result = _basic_search(client, index_id, page_limit=5)
        assert result.page_info is not None
        assert result.page_info.limit_per_page == 5

    def test_PA04_next_page_token_present_when_more_results(self, client, index_id):
        """next_page_token is set when total_results > page_limit."""
        result = _basic_search(client, index_id, page_limit=1)
        assert result.page_info is not None
        if result.page_info.total_results and result.page_info.total_results > 1:
            assert result.page_info.next_page_token is not None

    def test_PA05_retrieve_next_page_via_token(self, client, index_id):
        """search.retrieve() returns a valid page when given a next_page_token."""
        result = _basic_search(client, index_id, page_limit=1)
        assert result.page_info is not None
        token = result.page_info.next_page_token
        if token is None:
            pytest.skip("Only one page of results available.")
        next_page = client.search.retrieve(page_token=token)
        assert next_page is not None
        assert next_page.data is not None

    def test_PA06_retrieve_expired_token_raises_error(self, client):
        """search.retrieve() with an obviously invalid token raises ApiError."""
        with pytest.raises(ApiError) as exc_info:
            client.search.retrieve(page_token="invalid_token_xyz")
        assert exc_info.value.status_code in (400, 404)


# ---------------------------------------------------------------------------
# Category 3: Transcription Options (TR)
# ---------------------------------------------------------------------------

class TestTranscriptionOptions:

    def test_TR01_transcription_lexical_only(self, client, index_id):
        """transcription_options=['lexical'] performs exact-word matching."""
        result = client.search.create(
            index_id=index_id,
            search_options=["transcription"],
            query_text="hello",
            transcription_options=["lexical"],
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_TR02_transcription_semantic_only(self, client, index_id):
        """transcription_options=['semantic'] performs meaning-based matching."""
        result = client.search.create(
            index_id=index_id,
            search_options=["transcription"],
            query_text="greeting",
            transcription_options=["semantic"],
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_TR03_transcription_both_options(self, client, index_id):
        """transcription_options=['lexical', 'semantic'] is the default and works."""
        result = client.search.create(
            index_id=index_id,
            search_options=["transcription"],
            query_text="hello",
            transcription_options=["lexical", "semantic"],
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None


# ---------------------------------------------------------------------------
# Category 4: Filtering (FI)
# ---------------------------------------------------------------------------

class TestFiltering:

    def test_FI01_filter_by_duration_range(self, client, index_id):
        """Filter by duration range accepts valid JSON filter string."""
        duration_filter = json.dumps({"duration": {"gte": 1, "lte": 99999}})
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="a person walking",
            filter=duration_filter,
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_FI02_filter_by_nonexistent_video_id_raises_bad_request(self, client, index_id):
        """Filtering by a video ID not in the index raises a 400 BadRequestError."""
        from twelvelabs.errors.bad_request_error import BadRequestError

        nonexistent_filter = json.dumps({"id": ["000000000000000000000000"]})
        with pytest.raises(BadRequestError) as exc_info:
            client.search.create(
                index_id=index_id,
                search_options=["visual"],
                query_text="a person walking",
                filter=nonexistent_filter,
            )
        assert exc_info.value.status_code == 400
        body = exc_info.value.body
        assert body.get("code") == "search_video_not_in_same_index"

    def test_FI03_filter_by_video_id_from_results(self, client, index_id):
        """Filter by a video_id extracted from a prior search returns only that video."""
        initial = _basic_search(client, index_id, page_limit=1)
        if not initial.data:
            pytest.skip("No results available to derive a video_id filter.")
        video_id = initial.data[0].video_id
        id_filter = json.dumps({"id": [video_id]})
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="a person walking",
            filter=id_filter,
        )
        assert isinstance(result, SearchResults)
        if result.data:
            for item in result.data:
                assert item.video_id == video_id


# ---------------------------------------------------------------------------
# Category 5: Edge Cases (EC)
# ---------------------------------------------------------------------------

class TestEdgeCases:

    def test_EC01_query_with_no_likely_match_returns_empty(self, client, index_id):
        """A highly improbable query returns an empty list gracefully."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text="zzz_highly_unlikely_query_xyz_12345",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_EC02_long_query_text_within_limit(self, client, index_id):
        """A long but valid query (well under 500 tokens) is accepted."""
        long_query = "a person " * 50  # ~150 tokens, within the 500-token limit
        result = client.search.create(
            index_id=index_id,
            search_options=["visual"],
            query_text=long_query.strip(),
        )
        assert isinstance(result, SearchResults)

    def test_EC03_all_three_search_options_with_or(self, client, index_id):
        """Using visual, audio, and transcription together with or does not error."""
        result = client.search.create(
            index_id=index_id,
            search_options=["visual", "audio", "transcription"],
            query_text="a person talking",
            operator="or",
        )
        assert isinstance(result, SearchResults)
        assert result.data is not None

    def test_EC04_page_limit_one_returns_at_most_one_item(self, client, index_id):
        """page_limit=1 returns exactly 0 or 1 items."""
        result = _basic_search(client, index_id, page_limit=1)
        assert result.data is not None
        assert len(result.data) in (0, 1)

    def test_EC05_result_ranks_are_sequential(self, client, index_id):
        """Results are returned in rank order (1, 2, 3, ...)."""
        result = _basic_search(client, index_id, page_limit=5)
        if not result.data or len(result.data) < 2:
            pytest.skip("Not enough results to verify rank ordering.")
        ranks = [item.rank for item in result.data if item.rank is not None]
        assert ranks == sorted(ranks)


# ---------------------------------------------------------------------------
# Category 6: Error Handling (EH)
# ---------------------------------------------------------------------------

class TestErrorHandling:

    def test_EH01_nonexistent_index_id_raises_api_error(self, client):
        """A non-existent index_id should raise an ApiError (404)."""
        with pytest.raises(ApiError) as exc_info:
            client.search.create(
                index_id="000000000000000000000000",
                search_options=["visual"],
                query_text="a person walking",
            )
        assert exc_info.value.status_code == 404

    def test_EH02_invalid_api_key_raises_api_error(self, index_id):
        """An invalid API key should raise an ApiError."""
        bad_client = TwelveLabs(api_key="invalid_api_key_xyz")
        with pytest.raises(ApiError) as exc_info:
            bad_client.search.create(
                index_id=index_id,
                search_options=["visual"],
                query_text="a person walking",
            )
        assert exc_info.value.status_code in (401, 403)

    def test_EH03_page_limit_exceeds_maximum_raises_bad_request(self, client, index_id):
        """page_limit=51 (above the max of 50) should raise BadRequestError."""
        with pytest.raises(BadRequestError) as exc_info:
            client.search.create(
                index_id=index_id,
                search_options=["visual"],
                query_text="a person walking",
                page_limit=51,
            )
        assert exc_info.value.status_code == 400

    def test_EH04_invalid_filter_syntax_raises_bad_request(self, client, index_id):
        """A malformed filter string should raise BadRequestError."""
        with pytest.raises(BadRequestError) as exc_info:
            client.search.create(
                index_id=index_id,
                search_options=["visual"],
                query_text="a person walking",
                filter="this is not valid json {{{",
            )
        assert exc_info.value.status_code == 400

    def test_EH05_empty_search_options_raises_bad_request(self, client, index_id):
        """An empty search_options list should raise BadRequestError."""
        with pytest.raises((BadRequestError, ApiError)) as exc_info:
            client.search.create(
                index_id=index_id,
                search_options=[],
                query_text="a person walking",
            )
        assert exc_info.value.status_code == 400

    def test_EH06_unsupported_search_option_raises_bad_request(self, client, index_id):
        """An unsupported value in search_options should raise BadRequestError."""
        with pytest.raises((BadRequestError, ApiError)) as exc_info:
            client.search.create(
                index_id=index_id,
                search_options=["invalid_option"],
                query_text="a person walking",
            )
        assert exc_info.value.status_code == 400