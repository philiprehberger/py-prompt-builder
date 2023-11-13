# philiprehberger-prompt-builder

[![Tests](https://github.com/philiprehberger/py-prompt-builder/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-prompt-builder/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-prompt-builder.svg)](https://pypi.org/project/philiprehberger-prompt-builder/)
[![GitHub release](https://img.shields.io/github/v/release/philiprehberger/py-prompt-builder)](https://github.com/philiprehberger/py-prompt-builder/releases)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-prompt-builder)](https://github.com/philiprehberger/py-prompt-builder/commits/main)
[![License](https://img.shields.io/github/license/philiprehberger/py-prompt-builder)](LICENSE)
[![Bug Reports](https://img.shields.io/github/issues/philiprehberger/py-prompt-builder/bug)](https://github.com/philiprehberger/py-prompt-builder/issues?q=is%3Aissue+is%3Aopen+label%3Abug)
[![Feature Requests](https://img.shields.io/github/issues/philiprehberger/py-prompt-builder/enhancement)](https://github.com/philiprehberger/py-prompt-builder/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

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

### Conditional Content

```python
use_examples = True

messages = (
    Prompt()
    .system("You are a helpful assistant.")
    .conditional(use_examples, "user", "Here are some examples...")
    .conditional(use_examples, "assistant", "I understand the examples.")
    .user("Now answer my question: {question}")
    .render(question="What is Python?")
)
```

### Prompt Composition

```python
# Build reusable prompt fragments
preamble = Prompt().system("You are a coding assistant.").user("Use Python 3.12+.")
task = Prompt().user("Write a function that {task}")

# Merge fragments into a single prompt
combined = preamble.merge(task)
messages = combined.render(task="sorts a list")
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

| Function / Class | Description |
|------------------|-------------|
| `Prompt` | Fluent builder for constructing LLM message lists |
| `.system(content)` | Add a system message |
| `.user(content)` | Add a user message |
| `.assistant(content)` | Add an assistant message |
| `.message(role, content)` | Add a message with any role |
| `.example(user, assistant)` | Add a few-shot example pair |
| `.conditional(include, role, content)` | Conditionally add a message if `include` is truthy |
| `.merge(other)` | Create a new Prompt combining messages from self and other |
| `.render(**kwargs)` | Render with variable substitution, returns list of dicts |
| `.render_messages(**kwargs)` | Render and return Message objects |
| `.estimate_tokens(**kwargs)` | Rough token count (~4 chars/token) |
| `PromptTemplate` | Reusable prompt template with default values |
| `Message` | A single message with role and content |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this package useful, consider giving it a star on GitHub — it helps motivate continued maintenance and development.

[![LinkedIn](https://img.shields.io/badge/Philip%20Rehberger-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/in/philiprehberger)
[![More packages](https://img.shields.io/badge/more-open%20source%20packages-blue)](https://philiprehberger.com/open-source-packages)

## License

[MIT](LICENSE)
