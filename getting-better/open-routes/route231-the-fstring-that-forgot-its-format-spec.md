# OPEN ROUTE #231 — THE F-STRING THAT FORGOT ITS FORMAT SPEC (and its `!r` conversion)

**Status: OPEN (gen #36, 2026-10-12), Severity 1.** Found by the W-SB report author
(`getting-better/string-builder-wall.md`, point 6) while censusing string-builder constructs;
re-reproduced by the driver at HEAD 11834d83.

## Witnesses (PROVED at HEAD — "Verification SUCCESS! All contracts formally proven")

    #@ requires b == 10
    #@ ensures \result == 1
    def f(b: int) -> int:
        if f"{b:02x}" == f"{b}":      # CPython: "0a" == "10" -> False, returns 0
            return 1
        return 0

    #@ ensures \result == 1
    def f(s: str) -> int:
        if f"{s!r}" == f"{s}":        # CPython: "'x'" == "x" -> False, returns 0
            return 1
        return 0

## Mechanism
`src/pycsl/frontend/Module5_IREmitter.py::_py_expr_fstring` lowers an `ast.FormattedValue` to
`self._py_expr_to_ir(v.value)` and DISCARDS `v.format_spec` and `v.conversion`. So `f"{b:02x}"` and
`f"{b}"` produce the same IR and the same WhyML term, and their equality is a theorem.

## Repair direction
`f"{v!c:spec}"` is by definition `format(<conv>(v), spec)` (conv in repr/str/ascii). Carry the spec
and conversion into the IR and lower them to terms that are NOT identified with the plain
rendering (spec-keyed / conversion-keyed opaque string functions), or refuse fail-closed.
