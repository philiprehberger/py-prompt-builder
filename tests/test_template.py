"""Tests for the PromptTemplate class."""

from philiprehberger_prompt_builder import PromptTemplate


class TestPromptTemplate:
    def test_basic_render(self):
        t = PromptTemplate(system="Be helpful.", user="Hello")
        result = t.render()
        assert len(result) == 2
        assert result[0] == {"role": "system", "content": "Be helpful."}
        assert result[1] == {"role": "user", "content": "Hello"}

    def test_with_variables(self):
        t = PromptTemplate(
            system="You are a {role}.",
            user="Tell me about {topic}.",
        )
        result = t.render(role="teacher", topic="Python")
        assert result[0]["content"] == "You are a teacher."
        assert result[1]["content"] == "Tell me about Python."

    def test_defaults(self):
        t = PromptTemplate(
            system="You are a {role}.",
            defaults={"role": "assistant"},
        )
        result = t.render()
        assert result[0]["content"] == "You are a assistant."

    def test_kwargs_override_defaults(self):
        t = PromptTemplate(
            system="You are a {role}.",
            defaults={"role": "assistant"},
        )
        result = t.render(role="teacher")
        assert result[0]["content"] == "You are a teacher."

    def test_with_examples(self):
        t = PromptTemplate(
            system="Classify.",
            user="{text}",
            examples=[("good", "positive"), ("bad", "negative")],
        )
        result = t.render(text="okay")
        assert len(result) == 6
        assert result[0]["role"] == "system"
        assert result[1]["role"] == "user"
        assert result[1]["content"] == "good"
        assert result[2]["role"] == "assistant"
        assert result[5]["content"] == "okay"

    def test_with_assistant(self):
        t = PromptTemplate(assistant="I understand.")
        result = t.render()
        assert result == [{"role": "assistant", "content": "I understand."}]

    def test_extend(self):
        t = PromptTemplate(
            system="You are a {role}.",
            defaults={"role": "assistant"},
        )
        extended = t.extend(role="teacher")
        result = extended.render()
        assert result[0]["content"] == "You are a teacher."
        # Original unchanged
        original = t.render()
        assert original[0]["content"] == "You are a assistant."

    def test_estimate_tokens(self):
        t = PromptTemplate(system="Hello world", user="Tell me something")
        tokens = t.estimate_tokens()
        assert isinstance(tokens, int)
        assert tokens > 0
