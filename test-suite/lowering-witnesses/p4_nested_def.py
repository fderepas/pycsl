"""Witness driver — Pattern 4: nested `def rec(node):` inside a method.

PyCSL already hoists a nested `def` to a top-level WhyML `let` (lambda-lifting).
Two gaps remained:

  (a) A NON-reCURSIVE nested def already proved (witness `k_simple`).
  (b) A SELF-reCURSIVE nested def whose Python name is a WhyML reserved word
      (e.g. `rec`) hit a double bug: `whyml_ident("rec")` → `py_rec` renamed
      the DECLARATION, but `IRScanner.is_recursive(name, body)` scanned for the
      whyml-ident name `py_rec` while the body's `Call.func` held the IR name
      `rec` → `is_recursive` returned False → emitted `let py_rec` (not
      `let rec`) → "unbound function or predicate symbol 'py_rec'".

Fix (functions.py `_emit_function`): check `is_recursive` against BOTH the IR
name (`func["name"]`) and the whyml-ident name, so a reserved-word nested def
that calls itself emits `let rec py_rec` and type-checks.

Residual gap (honest): an int-recursing `let rec f (n:int) : int = ... f (n-1)`
now TYPE-CHECKS but Why3 still returns Unknown without an explicit `variant`
(Why3's default `let rec` termination is structural on algebraic-type args,
not on `int`). Variant inference for int-recursion is left to a future PR.
None of the 24 `_handle_*` methods in `statements.py` contain nested defs, so
this residual does not block the self-annotation goal.
"""
#@ requires True
#@ ensures True
def k_simple(node) -> int:
    def rec(n):
        return n
    return rec(node)
