# Fable response: `str(<int>) -> string` value-model wall

**Reviewer:** fable (independent). Branch ghost-assign-bc6, HEAD 5e7af18b.
**Method:** judgment formed ONLY from the repo + my own oracle runs; the report prose was not taken as
authority. Every verdict below is anchored to a tool artifact reproduced verbatim.

**Bottom line: VERDICT = CHEAP-BREAKABLE.** CLAIM A CONFIRMED, CLAIM B (corpus-inertness) CONFIRMED.
A faithful `val str_of_int (x: int) : string` replaces the int-erased `str_conv` model, typechecks, and is
**corpus-byte-diff-0 across all 767 swept files** (empty diff, exit 0). It is an abstract uninterpreted `val`
(no `ensures`) — NOT a new axiom; the 3-axiom ledger is untouched. One caveat: a subset (~2-3) of the string
helpers has a *second, independent* blocker (tuple-of-string-literal iteration → vacuous `int 0`); those are
BOUNDARY, not cheap, and must be excluded from the cheap yield.

---

## The source of the model (independent inspection)

`src/pycsl/module6_whyml/expressions.py:4709-4754`, the `func_name in ("str","repr","format","int","bool","abs")`
arm. The fall-through at the end:

```python
4752            wf = whyml_ident(func_name)
4753            self._add_abstract_op(f"val {wf}_conv (x: int) : int")
4754            return f"({wf}_conv {args[0]})"
```

For `func_name == "str"`, `whyml_ident("str") == "str"`, so a `str(<int>)` (arg NOT recognized as a string by
`_is_string_expr`) emits `val str_conv (x: int) : int` and lowers to `(str_conv <arg>)` — an **int-valued**
expression. `str(<string>)` is separately the identity (line 4739), and `repr(<string>)` is `str_repr_op:
string->string` (line 4748). Only `str(<int>)` is int-erased. This is exactly the report's CLAIM A model.

The live emitter helpers this blocks (`src/pycsl/module6_whyml/expressions.py`): `_coerce_str_arg` (433),
`_str_operand_to_int` (513), `_coerce_to_int` (531), the eq-hash helper (2515) — all do
`return str(stable_hash(whyml_str))`, i.e. they render an int hash to its decimal Python `str` and return it in a
`-> str` slot. Python `str(int)` here is genuinely `int -> string`; the PyCSL model `str_conv: int->int` is simply
unfaithful, which is why self-annotating these `-> str` helpers cannot typecheck.

---

## 1. CLAIM A verdict — CONFIRMED

`str(<int>)` in a `-> str` helper is int-erased and hits the int-in-string-slot typecheck error.

Oracle (spike `to_ident(n:int)->str: return str(n)`, then reverted):

```
$ .venv/bin/python3 src/pycsl/pycsl.py --no-proof --keep-mlw spikeA.py
[level] L1 ✓  L2 ✓  L3-tc ✗
[!] Emitted WhyML does NOT type-check (L3-tc failed) — NOT a success:
  spikeA.mlw, line 14, characters 4-16:
  This expression has type int, but is expected to have type string
```

Emitted `.mlw` (verbatim):

```whyml
  val str_conv (x: int) : int

  let to_ident (n: int) : string
    ensures  { (result <> "") }
  =
    (str_conv n)
```

`(str_conv n) : int` fed into the `string` return channel → hard typecheck error. **CLAIM A CONFIRMED.**

---

## 2. CLAIM B verdict (corpus-inertness) — CONFIRMED corpus-inert (the decisive result)

### 2a. No committed or freshly-swept corpus `.mlw` emits `str_conv`.

```
$ grep -rln "str_conv" --include="*.mlw" .        # committed fixtures (167 tracked *.mlw)
(no output)

$ PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh .../strwall_base
emitted 767 into .../strwall_base (7 jobs)

$ grep -rln "str_conv"   .../strwall_base   ;  # -> (no output)
$ grep -rln "str_to_int" .../strwall_base   ;  # -> (no output)
$ grep -rln "_conv"      .../strwall_base   ;  # -> (no output)
$ grep -rln "str_repr_op" .../strwall_base  ;  # -> 0487.mlw only (repr, string->string — unrelated)
```

Across all 767 emitted corpus programs there is **zero** `str_conv` / `str_to_int` / `*_conv`. No reference
corpus program relies on `str()`-of-int-in-a-string-context. The model is exercised ONLY by the emitter's own
self-annotation (the `str(stable_hash(...))` helpers), never by corpus source.

### 2b. The faithful fix typechecks AND leaves corpus emission byte-identical.

Spike (reverted after measurement): replace the `func_name=="str"` fall-through with
`self._add_abstract_op("val str_of_int (x: int) : string"); return f"(str_of_int {args[0]})"`.

Same `to_ident` helper now typechecks:

```
[level] L1 ✓  L2 ✓  L3-tc ✓
  val str_of_int (x: int) : string
  let to_ident (n: int) : string  ensures { (result <> "") } = (str_of_int n)
```

Full corpus sweep WITH the fix, diffed against the baseline sweep:

```
$ PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh .../strwall_fix
emitted 767 into .../strwall_fix (7 jobs)
$ diff -rq .../strwall_base .../strwall_fix
exit=0    (empty diff -> 767 files byte-identical)
```

**CLAIM B CONFIRMED: `str_conv` is emitter-only. A faithful `str_of_int: int->string` model is
corpus-byte-diff-0.** This is the CHEAP path, not the no-more-int build.

### 2c. Ledger check.
`val str_of_int (x: int) : string` is an abstract uninterpreted `val` with no `ensures` (like the existing
`str_repr_op`) — an opaque function, NOT an axiom. The 3-axiom ledger is unchanged. (Constraint §4 satisfied.)

---

## 3. VERDICT: CHEAP-BREAKABLE (for the pure-`str(int)` string-helper class)

### Yield estimate
Trusted stubs in the self-annotation mirror (independent count):

```
$ grep -c trusted src/self-annotate/src/module6_whyml/expressions.py   -> 57
$ grep -c trusted src/self-annotate/src/module6_whyml/statements.py    -> 61
```

118 trusted total (report's "~52 + ~47" is the same population, minor drift). These split into two DISJOINT
classes:

- **str(int) string-helper class (~13, per report):** `-> str` helpers whose sole conversion blocker is
  `str(<int>)`-into-string. The `str_of_int` fix unblocks these plus `_py_expr_fstring` (`str(v.value)`). This is
  the CHEAP-BREAKABLE cluster — est. **~13-15 markers**, corpus-byte-diff-0, one abstract val, no new axiom.
- **deep-dict `.get("type")` reflection class (the remaining ~100):** int-erased generic-dict/`.values()` walkers.
  This is a SEPARATE generic-dict value-model wall; `str_of_int` does nothing for it. Do not credit it to this fix.

### Make-or-break spike (recommended, already validated above)
1. Emit `val str_of_int (x: int) : string` for `func_name=="str"` (2-line change at expressions.py:4752; keep the
   generic `*_conv` fall-through for `format/bool` etc.).
2. Convert ONE pure helper — `_coerce_str_arg` (expressions.py:433) — to a body-faithful stub; whole-file proof
   (`--fun` is unreliable per `emit-ir-conversion-lessons.md` §1).
3. Gate: full-corpus byte-diff 0 (confirmed 0 above) + non-vacuity via an observational fixture on the string
   result.

### Secondary tuple-of-string-literal gap — SEPARATE blocker for a ~2-3 helper subset, NOT incidental to them
The report's `("(Array.make", ...)` prefix tuples are a real, independent blocker for the helpers that iterate
them (`_str_operand_to_int`, expressions.py:513-533, with `array_prefixes`/`map_prefixes`). Oracle:

```
def has_prefix(s: str) -> bool:
    prefixes = ("(Array.make", "(Array.sub")
    for p in prefixes:
        if s.startswith(p): return True
    return False
```
emits:
```
val s_startswith_1 (x0: int) : int ...
let prefixes = ref 0 in          <-- tuple-of-string-literals collapses to int 0
prefixes := 0;
... let p = ref ((iter_get !prefixes !_idx_p)) in
```

Note this typechecks (L3-tc ✓) but is **vacuous** — the tuple is `int 0`, `startswith` is int->int. So it is a
faithfulness/non-vacuity blocker, not a typecheck wall. It is INCIDENTAL to the pure-`str(int)` helpers (433,
2515, fstring — no tuple iteration) but a GENUINE second blocker for the prefix-iterating subset. Classify that
subset as **BOUNDARY** and exclude it from the ~13 cheap yield; land it later with faithful tuple-of-string-literal
iteration.

### Recommendation
Proceed with the CHEAP-BREAKABLE `str_of_int` build for the pure-`str(int)` string-helper cluster (~13-15
markers, corpus-inert, no new axiom, spike already green). Fence off the prefix-iterating helpers and the deep-dict
reflection class as separate walls. This is NOT the multi-session no-more-int project.

---

### Reproduction ledger (all commands run by fable; spike edits reverted, tree clean)
- CLAIM A: single-file `str(n)` in `-> str` helper → `str_conv:int->int`, L3-tc ✗ "type int ... expected string".
- CLAIM B corpus grep: 0 `str_conv`/`str_to_int`/`_conv` in 167 committed + 767 swept `.mlw`.
- CLAIM B byte-diff: `diff -rq base fix` empty, exit 0 (767 files) with faithful `str_of_int` applied.
- Fix typecheck: `str_of_int:int->string` → L3-tc ✓.
- Secondary gap: tuple-of-string-literals → `ref 0`, `startswith` int->int (typechecks but vacuous).
- `git status --short`: only TODO / session.txt (pre-existing) + this response file. No src edits remain.
