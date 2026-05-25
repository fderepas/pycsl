"""Lean AST → pycsl_emit IR.

Mirrors rocq2pycsl.translator: binder absorption, `\\result`
substitution, `Nat`/`Int` quantifier handling, top-level ∧ split into
separate ensures clauses, `termination_by` → variant, `partial def`
→ diverges. Rejects type-class-polymorphic theorems per plan §5.7.
"""

from .lean import translate_function, FunctionContract

__all__ = ["translate_function", "FunctionContract"]
