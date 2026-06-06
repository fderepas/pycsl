"""conftest.py — pytest configuration for pycsl tests.

Adds src/pycsl to sys.path so that the bare-import style used by the
pycsl modules (e.g. `from errors import PyCSLParseError`) works when
running tests from the repo root.
"""
import sys
import os

# The pycsl modules use bare imports (e.g. `from errors import ...`),
# so src/pycsl must be on the path in addition to the package install.
_PYCSL_SRC = os.path.join(os.path.dirname(__file__), "..", "src", "pycsl")
if _PYCSL_SRC not in sys.path:
    sys.path.insert(0, os.path.abspath(_PYCSL_SRC))
