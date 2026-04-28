"""Type-safe prompt template builder for LLM APIs."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

__all__ = [
    "Message",
    "Prompt",
    "PromptTemplate",
    "PromptVersionStore",
]

Role = str  # "system", "user", "assistant"


@dataclass
class Message:
    """A single message in a prompt."""

    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


class Prompt:
    """Fluent builder for constructing LLM message lists."""

    def __init__(self) -> None:
        self._messages: list[Message] = []

    def system(self, content: str) -> Prompt:
        """Add a system message."""
        self._messages.append(Message(role="system", content=content))
        return self

    def user(self, content: str) -> Prompt:
        """Add a user message."""
        self._messages.append(Message(role="user", content=content))
        return self

    def assistant(self, content: str) -> Prompt:
        """Add an assistant message."""
        self._messages.append(Message(role="assistant", content=content))
        return self

    def message(self, role: Role, content: str) -> Prompt:
        """Add a message with any role."""
        self._messages.append(Message(role=role, content=content))
        return self

    def example(self, user: str, assistant: str) -> Prompt:
        """Add a few-shot example (user + assistant pair)."""
        self._messages.append(Message(role="user", content=user))
        self._messages.append(Message(role="assistant", content=assistant))
        return self

    def with_examples(self, examples: list[tuple[str, str]]) -> Prompt:
        """Add multiple few-shot examples at once.

        Each tuple is an (input, output) pair added as a user/assistant
        message pair.

        Args:
            examples: List of (input, output) tuples.

        Returns:
            Self for chaining.
        """
        for user_input, assistant_output in examples:
            self._messages.append(Message(role="user", content=user_input))
            self._messages.append(Message(role="assistant", content=assistant_output))
        return self

    def expect_json(self, description: str | None = None) -> Prompt:
        """Append an instruction requesting JSON output.

        Adds a system message telling the model to respond with valid JSON.

        Args:
            description: Optional description of the expected JSON structure.

        Returns:
            Self for chaining.
        """
        instruction = "Respond with valid JSON only. No additional text or explanation."
        if description:
            instruction += f" Expected structure: {description}"
        self._messages.append(Message(role="system", content=instruction))
        return self

    def expect_list(self, description: str | None = None) -> Prompt:
        """Append an instruction requesting a list output.

        Adds a system message telling the model to respond with a numbered
        or bulleted list.

        Args:
            description: Optional description of the expected list items.

        Returns:
            Self for chaining.
        """
        instruction = "Respond with a list only. One item per line, using numbered or bulleted format. No additional text."
        if description:
            instruction += f" Each item should be: {description}"
        self._messages.append(Message(role="system", content=instruction))
        return self

    def render(self, **kwargs: Any) -> list[dict[str, str]]:
        """Render all messages, substituting {placeholders} with provided values.

        Returns:
            List of message dicts ready for OpenAI/Anthropic APIs.
        """
        result = []
        for msg in self._messages:
            content = msg.content
            if kwargs:
                content = _interpolate(content, kwargs)
            result.append({"role": msg.role, "content": content})
        return result

    def render_messages(self, **kwargs: Any) -> list[Message]:
        """Render and return Message objects instead of dicts."""
        result = []
        for msg in self._messages:
            content = msg.content
            if kwargs:
                content = _interpolate(content, kwargs)
            result.append(Message(role=msg.role, content=content))
        return result

    @property
    def messages(self) -> list[Message]:
        """Get raw messages without rendering."""
        return list(self._messages)

    def conditional(self, include: bool, role: Role, content: str) -> Prompt:
        """Conditionally add a message.

        If include is truthy, add a message with the given role and content.
        If falsy, return self unchanged.

        Args:
            include: Whether to include the message.
            role: The message role (e.g., "system", "user", "assistant").
            content: The message content.

        Returns:
            Self for chaining.
        """
        if include:
            self._messages.append(Message(role=role, content=content))
        return self

    def merge(self, other: Prompt) -> Prompt:
        """Create a new Prompt containing messages from self and other.

        All messages from self are included first, followed by all messages
        from other. The system message from self takes priority; if self has
        no system message, the system message from other is preserved.

        Args:
            other: Another Prompt to merge in.

        Returns:
            A new Prompt with combined messages.
        """
        result = Prompt()

        self_system = [m for m in self._messages if m.role == "system"]
        other_system = [m for m in other._messages if m.role == "system"]
        self_non_system = [m for m in self._messages if m.role != "system"]
        other_non_system = [m for m in other._messages if m.role != "system"]

        # Use system message from self, or fall back to other
        system_msgs = self_system if self_system else other_system

        result._messages = (
            list(system_msgs)
            + list(self_non_system)
            + list(other_non_system)
        )
        return result

    def estimate_tokens(self, **kwargs: Any) -> int:
        """Approximate token count using whitespace/word heuristics.

        Uses a combination of word count and character count to estimate
        tokens. The heuristic assumes roughly 0.75 tokens per word (since
        many common words are single tokens, but longer words may be split).
        A minimum of character_count // 4 is used as a floor.

        Args:
            **kwargs: Variables for placeholder substitution before counting.

        Returns:
            Estimated token count as an integer.
        """
        rendered = self.render(**kwargs)
        total_chars = 0
        total_words = 0
        for msg in rendered:
            content = msg["content"]
            total_chars += len(content)
            total_words += len(content.split())
        # Heuristic: ~0.75 tokens per word, floored by chars // 4
        word_estimate = int(total_words * 0.75)
        char_estimate = total_chars // 4
        return max(word_estimate, char_estimate)

    def warn_if_over(self, limit: int, **kwargs: Any) -> list[str]:
        """Return human-readable warnings when the prompt may exceed *limit* tokens.

        Uses :meth:`estimate_tokens` for a heuristic count. The warnings include
        an "approaching the limit" advisory at 80% utilisation and an "exceeds
        the limit" warning above the limit. Returns an empty list when the
        estimate is comfortably under *limit*.

        Args:
            limit: Token budget to check against (e.g. a model's context window).
            **kwargs: Variables for placeholder substitution before counting.

        Returns:
            List of warning strings — empty if there is nothing to flag.
        """
        if limit <= 0:
            raise ValueError("limit must be positive")

        estimate = self.estimate_tokens(**kwargs)
        warnings: list[str] = []

        if estimate > limit:
            warnings.append(
                f"Prompt estimate {estimate} tokens exceeds limit of {limit}"
            )
        elif estimate >= int(limit * 0.8):
            warnings.append(
                f"Prompt estimate {estimate} tokens approaching limit of {limit}"
            )

        return warnings


class PromptTemplate:
    """Reusable prompt template with default values."""

    def __init__(
        self,
        system: str | None = None,
        user: str | None = None,
        assistant: str | None = None,
        examples: list[tuple[str, str]] | None = None,
        defaults: dict[str, Any] | None = None,
    ):
        self._system = system
        self._user = user
        self._assistant = assistant
        self._examples = examples or []
        self._defaults = defaults or {}

    def render(self, **kwargs: Any) -> list[dict[str, str]]:
        """Render the template with the given variables.

        Variables from kwargs override defaults.

        Returns:
            List of message dicts ready for LLM APIs.
        """
        merged = {**self._defaults, **kwargs}
        prompt = Prompt()

        if self._system:
            prompt.system(self._system)

        for user_msg, assistant_msg in self._examples:
            prompt.example(user_msg, assistant_msg)

        if self._user:
            prompt.user(self._user)

        if self._assistant:
            prompt.assistant(self._assistant)

        return prompt.render(**merged)

    def extend(self, **overrides: Any) -> PromptTemplate:
        """Create a new template with updated defaults."""
        new_defaults = {**self._defaults, **overrides}
        return PromptTemplate(
            system=self._system,
            user=self._user,
            assistant=self._assistant,
            examples=list(self._examples),
            defaults=new_defaults,
        )

    def estimate_tokens(self, **kwargs: Any) -> int:
        """Approximate token count using whitespace/word heuristics."""
        rendered = self.render(**kwargs)
        total_chars = 0
        total_words = 0
        for msg in rendered:
            content = msg["content"]
            total_chars += len(content)
            total_words += len(content.split())
        word_estimate = int(total_words * 0.75)
        char_estimate = total_chars // 4
        return max(word_estimate, char_estimate)


class PromptVersionStore:
    """Store and retrieve named prompt versions.

    Provides a simple registry for saving prompt snapshots by name,
    retrieving them later, and listing all stored versions.
    """

    def __init__(self) -> None:
        self._versions: dict[str, Prompt] = {}

    def save(self, name: str, prompt: Prompt) -> None:
        """Save a prompt snapshot under a given name.

        Creates a deep copy so that later mutations to the original prompt
        do not affect the stored version.

        Args:
            name: Version name (e.g., "v1", "experiment-a").
            prompt: The Prompt to store.
        """
        clone = Prompt()
        clone._messages = [
            Message(role=m.role, content=m.content)
            for m in prompt._messages
        ]
        self._versions[name] = clone

    def load(self, name: str) -> Prompt:
        """Retrieve a stored prompt version by name.

        Returns a deep copy so the stored version remains unchanged.

        Args:
            name: Version name to retrieve.

        Returns:
            A copy of the stored Prompt.

        Raises:
            KeyError: If no version exists with the given name.
        """
        if name not in self._versions:
            raise KeyError(f"No prompt version named '{name}'")
        stored = self._versions[name]
        clone = Prompt()
        clone._messages = [
            Message(role=m.role, content=m.content)
            for m in stored._messages
        ]
        return clone

    def list_versions(self) -> list[str]:
        """List all stored version names in insertion order.

        Returns:
            List of version name strings.
        """
        return list(self._versions.keys())

    def delete(self, name: str) -> None:
        """Delete a stored prompt version.

        Args:
            name: Version name to delete.

        Raises:
            KeyError: If no version exists with the given name.
        """
        if name not in self._versions:
            raise KeyError(f"No prompt version named '{name}'")
        del self._versions[name]


def _interpolate(text: str, variables: dict[str, Any]) -> str:
    """Replace {placeholders} with values from variables dict."""
    def replacer(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in variables:
            return str(variables[key])
        return match.group(0)  # Leave unreplaced

    return re.sub(r"\{(\w+)\}", replacer, text)
