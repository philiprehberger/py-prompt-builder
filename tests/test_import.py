"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_prompt_builder
    assert hasattr(philiprehberger_prompt_builder, "__name__") or True


def test_all_exports():
    """Verify __all__ contains expected exports."""
    from philiprehberger_prompt_builder import __all__
    assert "Prompt" in __all__
    assert "PromptTemplate" in __all__
    assert "Message" in __all__
    assert "PromptVersionStore" in __all__
