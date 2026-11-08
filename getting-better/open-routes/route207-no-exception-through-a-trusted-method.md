# Route #207 — `no_exception \all` proved through a trusted method that always raises

**Status:** CLOSED (gen #30). SEV-1. The decisive twin was already inside the tool.

## The witness

`1713_route207_no_exception_through_a_trusted_method.py` (expected FAIL):

```python
class Box:
    #@ ensures \result >= 0
    #@ \trusted
    def boom(self, n: int) -> int:
        raise ValueError("always")

    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result >= 0
    def safe(self, n: int) -> int:
        return self.boom(n)
```

PROVED. CPython: `Box().safe(1)` raises `ValueError`.

## The twin was in the tool

Three neighbouring spellings were ALREADY refused, which is what made the verdict
decisive rather than arguable:

| spelling                                          | verdict before the repair |
|---------------------------------------------------|---------------------------|
| module-level `\trusted` raiser, module-level caller | REFUSED                   |
| method raiser WITHOUT `\trusted`                    | FAILED (its body's `raise` propagates) |
| method raiser WITH `\trusted`                       | **PROVED**                |

`--strict-no-exception-propagation`, whose help text says *"any call from a
`no_exception`-enabled function to an abstract callee becomes an unsatisfiable VC"*, did
not change the verdict either — so its documented behaviour did not hold for this spelling.

## Where it came from

Route #161 inverted the default for `no_exception` callees: a call is allowed only if the
callee is *"a function or class of the verified program (its own contract speaks for it)"*
or on a whitelist of operations that cannot raise. A `\trusted` / `\abstract` callee IS a
function of the program — and nothing speaks for it: no body is lowered, and a bodyless
`val` carries no `raises`, so Why3 is told the call cannot raise. The method arm admitted
it on the strength of its NAME (`_tail161 in _tails161`).

## The repair

At route #161's own site: when the callee is a method, refuse if its name matches a
`trusted`/`abstract` function in the IR (`self.ir` carries the flags) and it is not one of
the whitelisted builtin method names.

## Controls

`1714_route207_no_exception_trusted_method_with_raises_control.py` (expected PASS): an
ordinary verified method called under `no_exception \all` still proves. The corpus-wide
`no_exception` regression sweep (134 files) was run separately and is recorded in the
probe ledger.
