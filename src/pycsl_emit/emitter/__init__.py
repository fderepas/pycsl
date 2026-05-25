"""emitter — libcst-based Python source rewriting.

locator.py finds a `def` node by Python qualname (matches `__qualname__`).
annotator.py inserts `#@` annotation lines immediately before the `def`,
with no blank line in between, preserving any existing leading comments.
"""

from .locator import find_function
from .annotator import annotate_function, annotate_source

__all__ = ["find_function", "annotate_function", "annotate_source"]
