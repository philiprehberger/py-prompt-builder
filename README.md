# philiprehberger-prompt-builder

[![Tests](https://github.com/philiprehberger/py-prompt-builder/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-prompt-builder/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-prompt-builder.svg)](https://pypi.org/project/philiprehberger-prompt-builder/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-prompt-builder)](https://github.com/philiprehberger/py-prompt-builder/commits/main)

Type-safe prompt template builder for LLM APIs.

## Installation

```bash
pip install philiprehberger-prompt-builder
```

## Usage

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
from philiprehberger_prompt_builder import Prompt

messages = (
    Prompt()
    .system("Classify the sentiment.")
    .example(user="I love this!", assistant="positive")
    .example(user="Terrible product.", assistant="negative")
    .user("{text}")
    .render(text="Pretty good actually")
)
```

### Batch Few-Shot Examples

```python
from philiprehberger_prompt_builder import Prompt

messages = (
    Prompt()
    .system("Translate English to French.")
    .with_examples([
        ("Hello", "Bonjour"),
        ("Goodbye", "Au revoir"),
        ("Thank you", "Merci"),
    ])
    .user("{text}")
    .render(text="Good morning")
)
```

### Output Format Instructions

```python
from philiprehberger_prompt_builder import Prompt

# Request JSON output
messages = (
    Prompt()
    .system("Extract structured data.")
    .user("Parse: {text}")
    .expect_json(description='{"name": string, "age": number}')
    .render(text="John is 30 years old")
)

# Request list output
messages = (
    Prompt()
    .system("Generate ideas.")
    .user("List 5 project ideas about {topic}")
    .expect_list()
    .render(topic="machine learning")
)
```

### Conditional Content

```python
from philiprehberger_prompt_builder import Prompt

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
from philiprehberger_prompt_builder import Prompt

preamble = Prompt().system("You are a coding assistant.").user("Use Python 3.12+.")
task = Prompt().user("Write a function that {task}")

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

messages = summarizer.render(content="Article text...")
messages = summarizer.render(content="...", tone="detailed", format="paragraphs")

verbose = summarizer.extend(tone="thorough", format="essay")
```

### Prompt Versioning

```python
from philiprehberger_prompt_builder import Prompt, PromptVersionStore

store = PromptVersionStore()

v1 = Prompt().system("You are helpful.").user("Answer: {question}")
store.save("v1", v1)

v2 = Prompt().system("You are a concise expert.").user("Answer briefly: {question}")
store.save("v2", v2)

prompt = store.load("v1")
messages = prompt.render(question="What is Python?")

store.list_versions()  # ["v1", "v2"]
```

### Token Estimation

```python
from philiprehberger_prompt_builder import Prompt

prompt = Prompt().system("You are helpful.").user("{text}")
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
| `.with_examples(examples)` | Add multiple few-shot examples from a list of (input, output) tuples |
| `.expect_json(description)` | Append instruction requesting JSON output |
| `.expect_list(description)` | Append instruction requesting list output |
| `.conditional(include, role, content)` | Conditionally add a message if `include` is truthy |
| `.merge(other)` | Create a new Prompt combining messages from self and other |
| `.render(**kwargs)` | Render with variable substitution, returns list of dicts |
| `.render_messages(**kwargs)` | Render and return Message objects |
| `.estimate_tokens(**kwargs)` | Approximate token count using word heuristics |
| `PromptTemplate` | Reusable prompt template with default values |
| `.extend(**overrides)` | Create a new template with updated defaults |
| `PromptVersionStore` | Store and retrieve named prompt versions |
| `.save(name, prompt)` | Save a prompt snapshot under a name |
| `.load(name)` | Retrieve a stored prompt version by name |
| `.list_versions()` | List all stored version names |
| `.delete(name)` | Delete a stored prompt version |
| `Message` | A single message with role and content |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-prompt-builder)

🐛 [Report issues](https://github.com/philiprehberger/py-prompt-builder/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-prompt-builder/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
