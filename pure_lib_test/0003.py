"""Concrete test 0003: pure_lib/warnings — warn, simplefilter, catch_warnings.

Tests all 4 symbols from calling.json: warn, simplefilter,
catch_warnings, _deprecated.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pure_lib.warn import warn, simplefilter, catch_warnings, _deprecated
from pure_lib.warn import _warnings_log, _filter_actions, _filter_categories


def test_warn_basic():
    _warnings_log.clear()
    _filter_actions.clear()
    _filter_categories.clear()
    rc = warn("test message")
    assert rc == 0, f"warn returned {rc}"
    assert len(_warnings_log) == 1, f"expected 1 warning, got {len(_warnings_log)}"
    assert _warnings_log[0][0] == "test message"
    print("PASS: 1 — warn basic")


def test_simplefilter_ignore():
    _warnings_log.clear()
    _filter_actions.clear()
    _filter_categories.clear()
    simplefilter("ignore")
    warn("should be ignored")
    assert len(_warnings_log) == 0, f"expected 0 warnings, got {len(_warnings_log)}"
    print("PASS: 2 — simplefilter ignore")


def test_simplefilter_error():
    _warnings_log.clear()
    _filter_actions.clear()
    _filter_categories.clear()
    simplefilter("error")
    try:
        warn("should raise")
        assert False, "expected exception"
    except Exception as e:
        assert str(e) == "should raise"
    print("PASS: 3 — simplefilter error")


def test_catch_warnings():
    _warnings_log.clear()
    _filter_actions.clear()
    _filter_categories.clear()
    simplefilter("default")
    with catch_warnings():
        simplefilter("ignore")
        warn("inside catch — should be ignored")
        assert len(_warnings_log) == 0
    # filters restored
    warn("after catch — should be collected")
    assert len(_warnings_log) == 1
    print("PASS: 4 — catch_warnings context manager")


def test_deprecated():
    _warnings_log.clear()
    _filter_actions.clear()
    _filter_categories.clear()
    _deprecated("old_func")
    assert len(_warnings_log) == 1
    assert "old_func" in _warnings_log[0][0]
    assert "deprecated" in _warnings_log[0][0]
    print("PASS: 5 — _deprecated helper")


if __name__ == '__main__':
    test_warn_basic()
    test_simplefilter_ignore()
    test_simplefilter_error()
    test_catch_warnings()
    test_deprecated()
    print("\nPASS: 0003 — all pure_lib/warnings tests passed")
