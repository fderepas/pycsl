"""Pure-Python warnings subset — only the API surface used by PyCSL.

Provides: warn(), simplefilter(), catch_warnings context manager,
and _deprecated() helper.

This is a minimal model: warnings are collected in a module-level list
rather than printed to stderr, making the behavior deterministic and
verifiable.
"""

# ── Warning filters ──────────────────────────────────────────────────

_filter_actions = []    # list of action strings
_filter_categories = [] # parallel list of category values
_warnings_log = []      # collected warnings for testing


#@ assigns \nothing
#@ ensures \result >= 0
def simplefilter(action, category=0, stacklevel=1, append=False):
    """Insert a simple warning filter entry."""
    if append:
        _filter_actions.append(action)
        _filter_categories.append(category)
    else:
        _filter_actions.insert(0, action)
        _filter_categories.insert(0, category)
    return 0


#@ assigns \nothing
def _get_action(category):
    """Return the action for a given warning category."""
    i = 0
    n = len(_filter_actions)
    #@ loop invariant 0 <= i
    #@ loop variant n - i
    while i < n:
        cat = _filter_categories[i]
        if cat == 0 or cat == category:
            return _filter_actions[i]
        i += 1
    return "default"


#@ assigns \nothing
#@ ensures \result == 0
def warn(message, category=0, stacklevel=1, source=None):
    """Issue a warning.

    In this pure-lib model, warnings are collected in _warnings_log
    rather than printed to stderr.
    """
    action = _get_action(category)
    if action == "error":
        raise Exception(message)
    if action == "ignore":
        return 0
    _warnings_log.append((message, category))
    return 0


#@ assigns \nothing
#@ ensures \result == 0
def _deprecated(name, message=0, remove=0, _version=0):
    """Mark something as deprecated — appends to warning log directly."""
    if message == 0:
        msg = f"{name} is deprecated"
    else:
        msg = message
    _warnings_log.append((msg, 0))
    return 0


# ── catch_warnings context manager ───────────────────────────────────

class catch_warnings:
    """Context manager that copies and restores the warning filter."""

    def __init__(self, record=False):
        self._record = record
        self._saved_actions = None
        self._saved_categories = None

    #@ assigns \nothing
    def __enter__(self):
        self._saved_actions = _filter_actions[:]
        self._saved_categories = _filter_categories[:]
        if self._record:
            _warnings_log.clear()
            return _warnings_log
        return None

    #@ assigns \nothing
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _filter_actions, _filter_categories
        _filter_actions = self._saved_actions
        _filter_categories = self._saved_categories
        return False
