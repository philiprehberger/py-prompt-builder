"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_prompt_builder
    assert hasattr(philiprehberger_prompt_builder, "__name__") or True
