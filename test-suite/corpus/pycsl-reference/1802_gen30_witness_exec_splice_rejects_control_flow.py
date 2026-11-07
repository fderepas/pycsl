r"""Test 1802 — WITNESS: the constant-`exec(...)` splice refuses CONTROL FLOW in the
spliced source.

`splice_constant_exec` replaces a constant-`exec` expression-statement with its parsed
body, so the spliced statements become part of the enclosing function. That is only sound
while they are straight-line: an `if`, a loop, an `import`, a `def`/`class` or a nested
`exec` would CHANGE THE CFG the rest of the pipeline has already reasoned about. The
whitelist refuses them by NODE TYPE and names the type it saw.

One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
Its sibling one line below — the NESTED-exec rejection — still has none, and not for want
of trying: a nested `exec` is refused FIRST by the name-value check ("a name's runtime
value is not the one the model reads"), which is lesson (n3) again.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result >= 0
def f(n: int) -> int:
    exec("if n > 0:\n    n = n + 1")
    return n
