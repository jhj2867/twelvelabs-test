# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python test project for exploring the [TwelveLabs](https://www.twelvelabs.io/) video understanding API. It uses the `twelvelabs` SDK to perform video search queries against a pre-configured index.

## Environment Setup

Copy `.env` and set the required variables:

```
TWELVELABS_API_KEY=<your api key>
TWELVELABS_INDEX_ID=<your index id>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Commands

Run all tests:

```bash
pytest
```

Run a single test:

```bash
pytest tests/test_search.py::test_search
```

## Architecture

- `utils/client.py` — Exports `get_client()`, which reads `TWELVELABS_API_KEY` from the environment and returns an authenticated `TwelveLabs` SDK client instance.
- `utils/config.py` — Exports `INDEX_ID`, read from `TWELVELABS_INDEX_ID` env var. Raises `ValueError` at import time if missing.
- `tests/` — pytest-based integration tests that call the real TwelveLabs API. Tests require valid credentials in `.env` and an index that already contains ingested video data.

Note: tests hit the live TwelveLabs API — there are no mocks. Running tests requires a valid API key and an index with video content.