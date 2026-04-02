"""Tests for the PromptVersionStore class."""

import pytest

from philiprehberger_prompt_builder import Prompt, PromptVersionStore


class TestPromptVersionStore:
    def test_save_and_load(self):
        store = PromptVersionStore()
        p = Prompt().system("Hello").user("World")
        store.save("v1", p)
        loaded = store.load("v1")
        assert loaded.render() == p.render()

    def test_load_returns_copy(self):
        store = PromptVersionStore()
        p = Prompt().system("Original")
        store.save("v1", p)
        loaded = store.load("v1")
        loaded.user("Added after load")
        reloaded = store.load("v1")
        assert len(reloaded.messages) == 1

    def test_save_stores_copy(self):
        store = PromptVersionStore()
        p = Prompt().system("Original")
        store.save("v1", p)
        p.user("Added after save")
        loaded = store.load("v1")
        assert len(loaded.messages) == 1

    def test_list_versions_empty(self):
        store = PromptVersionStore()
        assert store.list_versions() == []

    def test_list_versions(self):
        store = PromptVersionStore()
        store.save("alpha", Prompt().system("a"))
        store.save("beta", Prompt().system("b"))
        store.save("gamma", Prompt().system("c"))
        assert store.list_versions() == ["alpha", "beta", "gamma"]

    def test_overwrite_version(self):
        store = PromptVersionStore()
        store.save("v1", Prompt().system("First"))
        store.save("v1", Prompt().system("Second"))
        loaded = store.load("v1")
        assert loaded.render()[0]["content"] == "Second"
        assert store.list_versions() == ["v1"]

    def test_load_nonexistent_raises(self):
        store = PromptVersionStore()
        with pytest.raises(KeyError, match="No prompt version named 'missing'"):
            store.load("missing")

    def test_delete(self):
        store = PromptVersionStore()
        store.save("v1", Prompt().system("test"))
        store.delete("v1")
        assert store.list_versions() == []

    def test_delete_nonexistent_raises(self):
        store = PromptVersionStore()
        with pytest.raises(KeyError, match="No prompt version named 'nope'"):
            store.delete("nope")

    def test_multiple_independent_versions(self):
        store = PromptVersionStore()
        store.save("simple", Prompt().user("Hi"))
        store.save("complex", Prompt().system("Be detailed.").user("Explain {topic}"))
        simple = store.load("simple")
        complex_prompt = store.load("complex")
        assert len(simple.messages) == 1
        assert len(complex_prompt.messages) == 2
        assert complex_prompt.render(topic="AI")[1]["content"] == "Explain AI"
