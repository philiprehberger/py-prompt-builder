"""Type-safe prompt template builder for LLM APIs."""

from __future__ import annotations

import re
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Prompt", "PromptTemplate", "Message"]

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
        """Rough token count estimate (~4 chars per token)."""
        rendered = self.render(**kwargs)
        total_chars = sum(len(m["content"]) for m in rendered)
        return total_chars // 4


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
        """Rough token count estimate."""
        rendered = self.render(**kwargs)
        total_chars = sum(len(m["content"]) for m in rendered)
        return total_chars // 4


def _interpolate(text: str, variables: dict[str, Any]) -> str:
    """Replace {placeholders} with values from variables dict."""
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in variables:
            return str(variables[key])
        return match.group(0)  # Leave unreplaced

    return re.sub(r"\{(\w+)\}", replacer, text)
