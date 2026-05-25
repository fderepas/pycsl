"""Translate Gallina surface AST → pycsl_emit IR.

Owns the language-specific concerns: binder absorption, `\\result`
substitution, `nat` → `>= 0` constraints, top-level conjunction
splitting, divides → IR.Divides, measure → IR variant.
"""

from .gallina import translate_function, FunctionContract

__all__ = ["translate_function", "FunctionContract"]
