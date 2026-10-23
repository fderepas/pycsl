# OPEN ROUTE #231 — THE F-STRING THAT FORGOT ITS FORMAT SPEC (and its `!r` conversion)

**Status: REPAIRED (gen #36, 2026-10-12; opened OPEN same day), Severity 1.** Found by the W-SB report author
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

## Repair landed (branch r231)

* **Module 5** (`_py_expr_fstring`): a `FormattedValue` with a conversion and/or a spec now
  emits `{"type": "FormattedValue", "value": ..., "conversion": <code point>?,
  "format_spec": <FString>?}`; a plain `{v}` keeps the bare operand, so every f-string without
  `!c`/`:spec` has byte-identical IR (corpus + pyref byte-diff 0 MOVED; conformance goldens
  38/38 unchanged). A nested spec (`f"{x:{w}}"`) is itself a JoinedStr and recurses.
* **Module 6** (`_expr_to_whyml`, top, `\trusted` in the mirror): the part lowers to an OPAQUE
  `val function pycsl_format_<c>_<t>_h<hex(spec)> (x: <t>) : string` (no axiom), keyed
  INJECTIVELY by conversion (`n`/`s`/`r`/`a`), hex-encoded literal spec and operand type
  (`s` string / `i` int); a nested spec lowers to `pycsl_format_dyn_<c>_<t>_<st> (spec) (x)`,
  opaque in the spec term too. `{s!r}` with no spec on a str in program context reuses the
  existing `repr(s)` lowering's `str_repr_op` (same declaration), so `f"{s!r}"` and `repr(s)`
  coincide. Operands are passed raw (no `_coerce_to_int` array->0 collapse): a non-int/str
  operand fails the Why3 type check, fail-closed. `_is_string_expr` classifies the node as a
  string, consistent with the lowering.
* **Witnesses** 1932-1936, 1940 (FAIL; all PROVED at 3ca32b8d) and controls 1937-1939 (PASS at
  both). 1705/1706 keep FAIL/PASS.
