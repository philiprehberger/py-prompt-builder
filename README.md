# philiprehberger-prompt-builder

[![Tests](https://github.com/philiprehberger/py-prompt-builder/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-prompt-builder/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-prompt-builder.svg)](https://pypi.org/project/philiprehberger-prompt-builder/)
[![License](https://img.shields.io/github/license/philiprehberger/py-prompt-builder)](LICENSE)

Type-safe prompt template builder for LLM APIs.

## Installation

```bash
pip install philiprehberger-prompt-builder
```

## Usage

### Fluent Builder

```python
from philiprehberger_prompt_builder import Prompt

messages = (
    Prompt()
    .system("You are a helpful assistant.")
    .user("Summarize this article: {article}")
    .render(article="Long article text here...")
)
# [{"role": "system", "content": "You are a helpful assistant."},
#  {"role": "user", "content": "Summarize this article: Long article text here..."}]
```

### Few-Shot Examples

```python
messages = (
    Prompt()
    .system("Classify the sentiment.")
    .example(user="I love this!", assistant="positive")
    .example(user="Terrible product.", assistant="negative")
    .user("{text}")
    .render(text="Pretty good actually")
)
```

### Reusable Templates

```python
from philiprehberger_prompt_builder import PromptTemplate

summarizer = PromptTemplate(
    system="You are a {tone} summarizer. Output in {format}.",
    user="Summarize: {content}",
    defaults={"tone": "concise", "format": "bullet points"},
)

# Use with defaults
messages = summarizer.render(content="Article text...")

# Override defaults
messages = summarizer.render(content="...", tone="detailed", format="paragraphs")

# Create variant
verbose = summarizer.extend(tone="thorough", format="essay")
```

### Token Estimation

```python
prompt = Prompt().system("...").user("{text}")
estimated = prompt.estimate_tokens(text="Hello world")
```

## API

| Method | Description |
|--------|-------------|
| `.system(content)` | Add a system message |
| `.user(content)` | Add a user message |
| `.assistant(content)` | Add an assistant message |
| `.example(user, assistant)` | Add a few-shot example pair |
| `.render(**kwargs)` | Render with variable substitution → list of dicts |
| `.estimate_tokens(**kwargs)` | Rough token count (~4 chars/token) |


## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
