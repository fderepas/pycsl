"""Pure-Python re subset — only the API surface used by lib/json.

Provides: compile(), sub(), flags (VERBOSE, MULTILINE, DOTALL, DEBUG),
Pattern (with .match and .sub), Match (with .group, .groups, .end),
and PatternError / error.

Every compiled pattern is backed by a hand-written matcher, not a
general regex engine.  Only the seven patterns json actually uses are
supported; compiling an unknown pattern raises PatternError.
"""

from ._engine import compile, sub, RePattern, ReMatch  # noqa: F401
from ._engine import VERBOSE, MULTILINE, DOTALL, DEBUG  # noqa: F401
from ._engine import PatternError  # noqa: F401

Pattern = RePattern
Match = ReMatch
error = PatternError
