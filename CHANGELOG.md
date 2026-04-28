# Changelog

## 0.4.0 (2026-04-27)

- Add `Prompt.warn_if_over(limit)` returning warning strings when the estimated token count is approaching or exceeds a context window
- Returns warnings (not exceptions) so callers can decide their own gating behaviour

## 0.3.0 (2026-04-01)

- Add `with_examples()` for batch few-shot example insertion
- Add `expect_json()` and `expect_list()` for output format instructions
- Add `PromptVersionStore` for storing and retrieving named prompt versions
- Improve `estimate_tokens()` with word-based heuristic for better accuracy
- Add comprehensive test suite covering all public APIs

## 0.2.1 (2026-03-31)

- Standardize README to 3-badge format with emoji Support section
- Update CI checkout action to v5 for Node.js 24 compatibility

## 0.2.0 (2026-03-27)

- Add `Prompt.conditional()` for conditionally including messages without external if/else
- Add `Prompt.merge()` for composing modular prompt fragments into a single prompt

## 0.1.7 (2026-03-22)

- Add pytest and mypy configuration to pyproject.toml

## 0.1.5

- Add basic import test

## 0.1.4

- Add Development section to README

## 0.1.1

- Add project URLs to pyproject.toml

## 0.1.0 (2026-03-10)

- Initial release
