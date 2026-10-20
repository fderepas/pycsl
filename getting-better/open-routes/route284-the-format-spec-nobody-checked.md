# OPEN ROUTE #284 — f-STRING FORMAT SPECS ON int/str: THE #281 DIGIT-LIMIT TRIGGER AND INVALID-SPEC ValueError ARE NOT EMITTED
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 7; driver-reproduced at 83aa79bd (p223/p057/p063/p064/p062 rc=0; CPython ValueError).
Witnesses `witnesses-r284/`. (a) `f"{x:d}"`, `:5`, `:05d`, `:n`, `:,`, `:>10`, `v={x:d}` under `no_exception \all`: the #281
`("call","int_str")` guard is computed in the literal-spec branch (~expressions.py:19449) but its assert is never emitted
(corpus 3118 FAILs only because of its repr/!r lines — the witness over-claims coverage). (b) invalid specs raise ValueError in
CPython and are not modelled: `f"{x:s}"` / `f"{x:.2}"` on int, `f"{s:d}"` on str. Repair: emit the digit-limit assert for every
int decimal rendering spec (not `:b/:x/:o`), and refuse or trigger on every spec not valid for the operand's type.
