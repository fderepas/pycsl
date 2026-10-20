# OPEN ROUTE #291 — f-STRING OF A bool RENDERS LIKE THE int 0/1
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r291/`. fs009 `b = True; x = 1; return f"{b}" == f"{x}"` proves True (CPython "True" vs "1" -> False); fs026::f4 bool from a comparison. A bool is the int 0/1 in the model and a bare f-string field lowers to the uninterpreted int-keyed `str_of_int_hash`. Repair: bool-typed fields render as "True"/"False" (or a distinct opaque bool renderer), also for str()/format()/%s; census every int->str rendering site reachable by a bool.

## REPAIR (2026-10-20, executor rA off 7313506b; commit 79a2d92f)
Probe table (rc; CPython ground truth in each corpus file's `__main__`):

| shape (`b = True`, `x = 1`) | 7313506b | after |
|---|---|---|
| `f"{b}" == f"{x}"` (fs009 / 3346) | PROVED | FAIL (unproven) |
| `f"{b!r}" == f"{x!r}"` (3347) | PROVED | FAIL |
| `f"{b:}" == f"{x:}"` (empty spec, 3348) | PROVED | FAIL |
| `f"{True}" == f"{1}"` (3349) | PROVED | FAIL |
| `b = x == 1; f"{b}" == f"{1 if b else 0}"` (fs026::f4 / 3350) | PROVED | FAIL |
| `f"{b:{w}}" == f"{x:{w}}"`, `w = ""` (computed spec) | FAIL | FAIL |
| `str(b) == str(x)`, `repr(b) == repr(x)`, `"{}".format(b) == ...`, `format(b) == format(x)`, `f"v={b}" == f"v={x}"`, `str(b) + "a"` | FAIL (non-`function` `val`s) | FAIL |
| `"%s" % b == "%s" % x` | ill-typed | ill-typed |
| controls (3351): `f"{len(xs)}" == f"{1}"`; `f"{b:>5}" == f"{x:>5}"` (CPython `'    1'` both); `f"{n:>5}" == f"{n:>5}"`; 1706 `n = 5; f"{n}" == f"{n}"` | PASS | PASS |

Rule (inline at three sites; `_handle_fstring_expr` and `_expr_to_whyml` are mirror-`\trusted`; no new
def/field; ledger 3). An int-model operand of the two VALUE-KEYED renderers — the single-part f-string's
`str_of_int_hash` and the `FormattedValue` symbol `pycsl_format_<c>_i_h<spec>` / `pycsl_format_dyn_<c>_i_*`
— is classified: SHOWN bool (bool literal, comparison, `not`, `bool(...)`, a `bool`-typed name, a call
declared `-> bool`, `c if t else c'` over bool literals) -> its own opaque `str_of_bool_hash` /
`pycsl_format_<c>_b_*` (no int rendering can equal it); SHOWN exact int (int literal, `len/int/abs/ord/
hash/sum`, `-`/`//`/`<<`/`>>`/unary `-`/`~`, `+`/`*` over int literals, an `int`-typed name or `-> int`
call) -> unchanged; anything else -> a program `val` (`str_of_value_op`, `pycsl_format_<c>_u_*`, no
`function`: fresh per evaluation). An unannotated local (`Any` in the symbol table) is classified from its
bindings in the owning function: all plain `name = <rhs>`, each rhs shown bool (resp. int). Faithful per
conversion: a NON-EMPTY literal spec with no conversion formats a bool as its int (`format(True, ">5") ==
"    1"`, and `"%d" % True == "1"`), so that key is kept; empty spec / `!s` / `!r` / `!a` are bool-specific.
Census of the int->str sites reachable by a bool: `str()` (`val str_of_int`), `repr()`/`format()`
(`val *_conv`), `str.format` (`format_conv`), multi-part f-strings (`val str_concat`), the `-> str` /
`@mutable_state` f-string branch (`val int_to_string`) are non-`function` `val`s — never decided; `%`
formatting of a bool is ill-typed today. Only the two value-keyed families decided, and both are fixed.
Model assumption, not new: an `int`-typed parameter given `True` (`g(True) == g(1)` with `g(n: int) ->
str: return f"{n}"`) is the declared BUILTIN-EXACT assumption's case (bool is a dunder-overriding int
subclass) — measured FAIL anyway (the callee's result is not exposed).
Blast radius: corpus root 0 MOVED for this route, pyref 0. Mirror 1 MOVED: `frontend__pure_ast`
(`Comment.__repr__`'s `{self.text!r}` on a `getattr_comment` read of unknown type: `pycsl_format_r_i_h`
`val function` -> `pycsl_format_r_u_h` program `val`); type-checks (L3-tc rc=0); `--fun` cannot isolate it
(the same "unexpected 'variant' clause" at 7313506b); whole-file proof OWED (the method is `ensures True`).
Gates (logs under the rA scratchpad; all heavy jobs via heavy.sh): witnesses at 7313506b vs after in
the table; byte-diff-sweep base/after rc=0 (2510 / 2529 sources); byte-diff-compare root rc=0 with ONE
declared mover (1915, below), pyref rc=0 (2186/2186, 0 MOVED / 0 GONE / 0 APPEARED); mirror-emit-sweep
base/after rc=0, compare `--min-files 45`: 1 MOVED (`frontend__pure_ast`, route #291, below), 0 GONE,
0 APPEARED; check-self-annotate-sync.sh rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53);
refusal-witness census +15 rows (3340-3344 REFUSAL, 3346-3350/3352-3354/3356-3357 VERIFY-FAIL) via
`--append-new` (that run also found 234 pre-existing FAIL witnesses with no row at 7313506b — not
appended here, out of scope; reported to the driver); run-soundness-planes.sh (fast): see README gen #37.
Residuals: before this repair the `i` class meant "not shown str", so an int-hash-modelled str element
and an int of equal value also shared these two renderers; `i` now requires a SHOWN int, which closes that
conflation for these families as a side effect. No other known residual.
