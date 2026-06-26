STATUS: OPEN

# Convergence gap — iteration 3 (trusted / string-returning imported method call routing)

**Loop:** `config/skills/pycsl-stdlib-coverage` — surfaced during implementation of
`10-2006-convergence-spec-2.md` (Gap 2b), under ruling **R4 (DEFERRED — STOP-AND-GAP)**.
**Iteration:** N = 3.

Gap 2b (fieldless method-bearing class → unit-carrying record) is IMPLEMENTED and gated
(STATUS: DONE on spec-2): a fieldless, no-`__init__`, non-mixin, non-composer class with ≥1
real method now emits a record type_decl, so `ir_resolve._resolve_imported_classes` injects
its `<class>__*` method stubs and a constructed instance's method call resolves.

This doc records the TWO follow-on routing defects that spec-2 R4 deferred. Neither blocks
spec-2 (its gate driver `0701.py` uses a simple-bodied INT-returning method, which proves);
both block the *full* strmod driver upgrade (`pure_lib_test/formal_strmod.py` theorems #7-#10,
which call `Template.substitute` / `Formatter.format` etc.).

---

## Defect 3a — bodyless `#@ \trusted` imported method is INLINED instead of routed to its `val`

**Symptom.** `/tmp/probe_2b.py` constructs `Formatter()` and calls `fmt.format(f)`, where
`Formatter.format` is `#@ \trusted` (RST: full format-string interpretation, no SMT model).
After Gap 2b injects the stub, the importer's inliner (`frontend/ir_inline.py`) still tries to
INLINE the call rather than route it to the injected abstract `val formatter__format`. The
trusted method's "body" is the placeholder `return fmt`, so the inliner emits:

```
let _inl_res__inl1 = ref 0 in        (* int ref *)
_inl_res__inl1 := f;                 (* f : string  → assigned to an int ref *)
(iter_length !_inl_res__inl1)        (* wrong: bound to an unrelated abstract op *)
```

L3-tc fails: `This expression has type string, but is expected to have type int`.

**Where.** `frontend/ir_inline.py` — `InlinePass._expand` / `inline_stmts` /
`_hoist_calls_in_expr`. The inliner has no notion that an injected method carrying
`trusted: True` (set in `ir_resolve._resolve_imported_classes`, ir_resolve.py:368) must NOT be
inlined; it should be left in place as a contract-call and lowered against the emitted
`val <class>__<method>` (the same treatment a `#@ no_inline` callee already gets via
`InlinePass.no_inline`, ir_inline.py:267-271).

**Proposed fix.** When building the inliner's `no_inline` / skip set, ALSO add any injected
method whose IR carries `trusted: True` (i.e. route trusted imported methods to their `val`,
exactly like `no_inline`). The dependency IR already marks them (`mf["trusted"] = True`); the
inliner just needs to consult that flag. This is the literal "route trusted imported method
calls to the injected `val` instead of inlining" follow-on named in spec-2 §Gap-2b sub-issue.

---

## Defect 3b — inlined STRING-returning method binds its result to an `int` ref

**Symptom (independent of trusted-ness; pre-existing, NOT introduced by Gap 2b).**
A simple-bodied (non-trusted, tail/early-return) method that returns `str`, when inlined,
binds the result through an `int`-typed temp. Minimal repro on a class WITH fields (so this is
NOT specific to the Gap-2b fieldless shape):

```python
class Box:
    x: int = 0
    #@ ensures \result == s
    #@ assigns \nothing
    def echo(self, s: str) -> str:
        return s
b = Box()
#@ ensures \result == s
def drv(s: str) -> str:
    return b.echo(s)
```

emits `let _inl_res__inl1 = ref 0 in ... := s` (string into an int ref) → L3-tc
`This expression has type string, but is expected to have type int`. Same failure with the
fieldless `Formatter.format_field` (a `str`-returning simple-bodied method) once it is inlined.

**Where.** The inlined result temp (`_inl_res__inlN`, created in `ir_inline.py:275` /
bound at `ir_inline.py:248`) is lowered by Module6 with the default `int` ref initializer; the
inliner/Module6 do not propagate the callee's `return_annotation` (here `str` → Why3 `string`,
init witness `""`) onto the temp's type. A list/array-returning method is already handled
specially (statements.py ~L950: `_inl_res = arr_local` flows array-ness); the `str`/`string`
case has no analogous propagation.

**Proposed fix.** Propagate the inlined method's WhyML return type onto the `_inl_res__inlN`
temp so its ref initializer matches (`ref ""` for `string`, `ref 0.0` for `real`), mirroring
the array-ness propagation already present. Equivalently, type the temp from the callee's
`return_annotation` at inline time so Module6's local-type inference picks it up.

---

## Why this is gapped, not hacked

Per spec-2 R4, the implementation does NOT pre-route trusted methods nor patch the
string-result-ref path inside the spec-2 change set (both touch the inliner / Module6 local
typing, beyond the additive Gap-2a/2b emission edits, and risk perturbing the full-corpus
byte-diff). The spec-2 gate driver (`test-suite/corpus/pycsl-reference/0701.py`) deliberately
uses a simple-bodied INT-returning fieldless-class method, which routes cleanly and proves.
3a and 3b are the next iteration's scope; fixing them unblocks the `formal_strmod` #7-#10
REAL-instance theorems.
