"""PyCSL mock for pytest.

Provides trusted stubs for the pytest testing framework.
"""
_ = 0  # anchor

# ── Test collection and running ─────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def main(args: int) -> int:
    """Mock: run pytest programmatically."""
    return 0

# ── Markers ─────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def mark_parametrize(argnames: int, argvalues: int) -> int:
    """Mock: parametrize a test function."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mark_skip(reason: int) -> int:
    """Mock: skip a test."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mark_skipif(condition: int, reason: int) -> int:
    """Mock: conditionally skip a test."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mark_xfail(reason: int) -> int:
    """Mock: mark test as expected failure."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mark_usefixtures(fixturename: int) -> int:
    """Mock: use fixtures on a test."""
    return 0

# ── Fixtures ────────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def fixture(fixture_scope: int) -> int:
    """Mock: declare a test fixture."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def yield_fixture(fixture_scope: int) -> int:
    """Mock: declare a yielding fixture."""
    return 0

# ── Assertions ──────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def pytest_raises(expected_exception: int) -> int:
    """Mock: assert that a block raises an exception."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def warns(expected_warning: int) -> int:
    """Mock: assert that a block raises a warning."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def approx(expected: int) -> int:
    """Mock: approximate comparison for floating point."""
    return 0

#@ \trusted
#@ ensures \result == 0
def fail(msg: int) -> int:
    """Mock: explicitly fail a test."""
    return 0

#@ \trusted
#@ ensures \result == 0
def skip(msg: int) -> int:
    """Mock: skip a test at runtime."""
    return 0

#@ \trusted
#@ ensures \result == 0
def xfail(reason: int) -> int:
    """Mock: xfail at runtime."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def importorskip(modname: int) -> int:
    """Mock: import module or skip test."""
    return 0

# ── Temporary directories ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def tmpdir() -> int:
    """Mock: provide a temporary directory."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tmp_path() -> int:
    """Mock: provide a temporary path."""
    return 0

# ── Capturing ───────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def capsys() -> int:
    """Mock: capture sys.stdout/sys.stderr."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def capfd() -> int:
    """Mock: capture file descriptors."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def monkeypatch() -> int:
    """Mock: dynamic modification of objects."""
    return 0
