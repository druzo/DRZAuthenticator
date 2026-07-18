from version import __version__


def test_version_string():
    """Version is a string."""
    assert isinstance(__version__, str)


def test_version_value():
    """Version starts at 0.03."""
    assert __version__ == "0.03"
