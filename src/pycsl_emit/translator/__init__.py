"""translator — IR → PyCSL surface syntax (string form).

opmap.py defines the language-agnostic operator mapping. divides.py
handles the operational/existential/guarded forms of divisibility.
names.py performs identifier remapping. render.py is the walker that
emits a fully-parenthesized PyCSL expression string from an IR node.
"""

from .render import render
from .divides import DividesStyle, render_divides
from .names import NameMap

__all__ = ["render", "DividesStyle", "render_divides", "NameMap"]
