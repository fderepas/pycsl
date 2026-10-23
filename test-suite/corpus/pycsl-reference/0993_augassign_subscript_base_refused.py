"""Test 0993 — `a[i].f op= v` is REFUSED. ROUTE #23, and it came off
`bin/check-dropped-mutation.py`'s DROPPED ratchet of 1 — a RECORDED fail-open that had
never been probed.

`Module5_IREmitter._py_stmt_augassign` was an `if/elif/elif` with NO `else`. It named
three target shapes — `x op= v`, `self.f op= v`, `a[k] op= v` — and SILENTLY DROPPED
everything else. Measured, before this refusal, on exactly this file's body with
`#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 5. The emitted body was

    (get_v self.items[0])

— the `+= 5` is not in the model at all, only the read that follows it.

THE CONTROL IS WHAT MAKES THIS A GAP RATHER THAN A LIMITATION. The PLAIN twin
`self.items[0].v = 5` was ALREADY refused, by `_py_stmt_assign`, with its reason spelled
out: a `List[<record>]` element is emitted PURE/immutable (Why3 forbids a mutable element
inside `array`), so there is no sound `<-` write-back for `a[i].f`. The augmented form
inherits that boundary; it now inherits the refusal too. Two spellings of one mutation,
one of them refused and the other silently dropped, is precisely the shape this campaign
keeps finding.

The gate's own ratchet comment had argued that refusing this "would reject `pure_ast.py`
itself for every mirror that imports it". THAT PREMISE DOES NOT HOLD, and checking it is
what made the fix free: the single site is `pure_ast._merge_str_constants`'s
`out[-1].value += v.value`, which lives in the LIVE emitter (never lowered), and the
MIRROR's copy of that function is `\trusted` with a `pass` body, so it is not lowered
either.

CENSUS (AST scan of both corpora, `src/pycsl`, `src/self-annotate/src`, `src/pycsl_lib`
and `tests/`): 1310 augmented assignments — 1208 Name, 77 `self.f`, 25 `a[k]`, all
modelled. Exactly TWO fell off the end: the `pure_ast` site above and one in
`tests/to_annotate/`. ZERO in either corpus. So the refusal is byte-inert by measurement.

REOPENING CAPABILITY: a sound write-back for a mutable object reached through a subscript
— the same one `_py_stmt_assign`'s refusal names, and the same one routes #13/#17/#18 need.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class E:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0


class Box:
    #@ requires True
    #@ ensures True
    #@ assigns self.items
    def __init__(self) -> None:
        self.items: list = [E()]

    #@ requires \length(self.items) > 0 and self.items[0].v == 0
    #@ ensures \result == 0
    def bump(self) -> int:
        self.items[0].v += 5
        return self.items[0].v


if __name__ == "__main__":
    print(Box().bump())
