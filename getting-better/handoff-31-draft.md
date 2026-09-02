# HANDOFF — #31 (2026-09-02, WINDOW 3): **455 -> 445, six emitter capabilities, two NEW
# GATE PLANES and eleven conversions — but the two findings that matter are that the
# CANDIDATE PROBE was measuring the wrong function for 40% of the tree, and that a
# CONVERTED GENERATOR's `yield`ed values are dropped on the floor with no plane able to
# see it.**

## THE NUMBERS

| | markers | grep | offset | unattached | ledger |
|---|---|---|---|---|---|
| #31 start (`b3ad0507`) | 455 | 480 | 25 | 0 | 3 |
| **#31 end** | **445** | **470** | **25** | **0** | **3** |

Net -10 = ELEVEN conversions minus ONE deliberate RE-TRUST (`iter_child_nodes`, below).

| # | commit | markers | what |
|---|---|---|---|
| 0 | `93dffbb0` | — | INSTRUMENT: probe recorded the CONTINUATION of a wrapped why3 diagnosis |
| 1 | `24a11bcc` | 455 -> 454 | `re.sub`/`re.escape` string model + `_strip_all_parens` |
| 2 | `a36de8ca` + `1639cd79` | 454 -> 452 | `pathlib.Path` model + `_default_lean_dir` / `_default_rocq_dir` |
| 3 | `a05185f6` | 452 -> 451 | EVERY-RHS-STRING local fixpoint + `_mangled_name` |
| 4 | `27ab0c3f` | — | STRING SUBSCRIPT `s[i]` |
| 5 | (yield gate) | 451 -> 452 | `iter_child_nodes` RE-TRUSTED — an honest +1 |
| 6 | (os.path) | 452 -> 450 | `os.path` model + `_proof_reference_mlw_name` / `_find_why3_coq_lib` |
| 7 | `9dec2e15` + `592c753f` | 450 -> 447 | probe SIGNATURE-PRESERVING port + `_err` / `_parse_mutex_expr_str` / `_walk_body` |
| 8 | `7121d1a7` | — | a REFLECTED NODE LIST is a real `array`, not an opaque iterable |
| 9 | `ec12c362` | 447 -> 445 | the CROSS-MIXIN PROTOCOL-STUB FRAME FIXPOINT + `_emit_array_local_reassign` / `_seq_operand` |

## THE TWO FINDINGS THAT MATTER

### 1. LESSON (bi): THE PROBE PORTED THE LIVE `def` LINE, DISCARDING THE MIRROR'S SIGNATURE

`bin/probe-conversion-candidates.py` spliced the live def AND body over the mirror stub.
The mirror's signature is not decoration: **188 of the 466 `\trusted` stubs that have a
live counterpart — 40% — carry a REFINED model annotation the live source does not have.**

    mirror  def _emit_array_local_reassign(..., val_ir: "ExprIR", ...)
    live    def _emit_array_local_reassign(..., val_ir: Dict[str, Any], ...)
    mirror  def statement(self) -> "List[ExprIR]"
    live    def statement(self)                       # no return annotation at all

Those annotations are what SELECT the emit_ir reflection (`val_ir.get("type")` ->
`kind_of val_ir`), the record projection, the pyval carrier and the typed return. A real
conversion KEEPS them — it deletes the `#@ \trusted` line and swaps the BODY. So the probe
was measuring the un-annotated, int-erased twin of each stub: systematically HARDER than
the thing a conversion actually produces.

**Whole-tree re-census after the repair: CLEAN 2 -> 8.** `Module2_Parser`, which #30
measured as **25 stubs / 25 L3TC-FAIL / 0 CLEAN** and recorded as REFUTED, yields two —
and one of them, `_parse_mutex_expr_str`, carried an explicit *CERTIFIED BOUNDARY
(parser-tokenstream-impl.md GAP #2)* comment in the mirror. Its stale comment is now
corrected in place (lesson (az)).

The repair is guarded on the two PARAMETER LISTS agreeing; when they do not it falls back
to the legacy port and FLAGS `PARAM-LIST DIVERGES`, which is how gate plane #2 below was
found.

### 2. LESSON (bj): A `yield` LOWERS TO `let _ = 0 in ()` — AND NO PLANE COULD SEE IT

Module 6 has no generator model. `yield <v>` emits `let _ = 0 in ()` and the `def` becomes
an ordinary function. `frontend/pure_ast.iter_child_nodes` was CONVERTED AND PROVED in
relaunch #30 in exactly that state:

    def iter_child_nodes(node):            let iter_child_nodes (node: int) : unit
        for _name, field in ...:      =>     ...
            if isinstance(field, AST):       if (py_isinstance_AST_int_op field) then
                yield field                    let _ = 0 in ()      <-- the whole method

Every plane was green: L3-tc passes (a `unit` body is well typed); `check-untrusted-emitted`
passes (it IS a definition); `check-emitted-vacuity` passes (the body still reads `node` via
`iter_fields node`, and that probe is documented as a LOWER BOUND); shadowed-selfcalls
passes; the mirror byte-diff and both fidelity scripts are indifferent. The proof was real
and it established **nothing about what the generator yields**, which is its entire meaning.

`iter_child_nodes` is RE-TRUSTED (451 -> 452, and the count going UP for this reason is the
right outcome). `bin/check-yield-erasure.py` now makes the class unbankable.

## THE TWO NEW GATE PLANES

### `bin/check-yield-erasure.py`
A converted mirror function whose body contains a VALUE-carrying `yield` must be emitted in
a form that can carry the values. Two mechanical symptoms, either of which fails: the
emitted definition returns `unit`, or its body contains `let _ = 0 in ()`.
State: **0 value-erasing · 2 suspension-dropping (ratchet 2) · 1 genuinely modelled.**
- MODELLED: `ir_inline._walk_dicts` — a real recognizer emits
  `let rec _walk_dicts (obj: pyval) : list pyval` with a genuine `Cons`.
- SUSPENSION (ratchet, not a failure): `_Unparser.block` / `_Unparser.delimit` are
  `@contextmanager`s whose VALUELESS `yield` drops no value but does drop the suspension —
  the emitted body runs the pre- and post-yield effects back to back with the caller's
  `with`-body nowhere. Lowering that ratchet needs a context-manager model.
NEGATIVE-TESTED (lesson (bg)): re-converting `iter_child_nodes` makes it exit 1.

### `bin/check-mirror-signature-drift.py`
The fidelity scripts compare the BODY of every UN-TRUSTED method. A `\trusted` stub has no
body — and its INTERFACE is its entire content. Nothing checked it.
**16 `\trusted` stubs disagree with the live parameter list; 0 converted methods do.**
- **10 MISSING a live parameter**: `_handle_dotted_call` declares `(self, func_name, args)`
  while the live signature has been `(self, func_name, args, arg_irs)` since #29 added
  `arg_irs`; `ir_resolve.resolve` is missing `import_paths`; `_m5_get_type_name` and
  `_normalize_union_annotation` are missing `dedup`; `_emit_first_assign` is missing
  `local_refs`; also `_handle_join_call`, `_handle_isinstance`, `_call_record_constructor`,
  `scc.sort_functions_by_scc`, `auto_trust._build_witness_str`.
- **6 pure RENAMES** (`expr` where the live binder is `node`): `_handle_binop`,
  `_handle_call_expr`, `_handle_subscript`, `_handle_attribute_expr`, `_handle_proj_expr`,
  `_handle_ctor_payload_expr`. Harmless to the model, but they BLOCK the
  signature-preserving port, so those six cannot be measured at all.
  **MEASURED (worktree spike, not landed): renaming all six makes them measurable and NONE
  of them becomes CLEAN** — the rename buys measurement, not markers. Their real blockers
  are `int` vs `PyCSL_Program.<record>` (three of them) and `_check_union_gt1`.
A CONVERTED method that drifts is a HARD failure, not a ratchet. Negative-tested.

## THE FIVE CAPABILITIES (all fail-closed; corpus byte-diff 0 for every one)

1. **`re.sub` / `re.escape` -> faithful `string` ops.** `re_sub_op` is a `val function`
   (deterministic — exactly what Python guarantees for default `count`/`flags`); NO content
   law. `re_escape_op` adds `length result >= length s` (escaping only inserts backslashes).
   Fail-closed on a keyword arg, a wrong arity, a compiled-pattern receiver, and — the
   important one — a CALLABLE `repl`, whose result is not a function of the argument values
   the model can see. Three of `normalize.py`'s own `re.sub` sites take a lambda and stay
   opaque BY DESIGN.
2. **The `pathlib.Path` value model.** `Path` (bare / dotted / quoted / `Optional[Path]`)
   resolves to the SAME `"str"` tag as `str` in Module5 (`_m5_path_ann_tag`), so every
   existing string mechanism applies for free. `p / q` -> `path_join_op`; `.parent`/`.stem`/
   `.name`/`.suffix` -> `path_*_op`. **Both rules are licensed by a fail-closed argument:
   `str / str` is a TypeError in Python and a Python `str` has none of those attributes, so
   a string-typed operand can only be a `Path`.** NO length or prefix law: an ABSOLUTE right
   operand discards the left (`Path("a") / "/b" == "/b"`).
   **This fixed a WRONG LOWERING**: path composition was going through the WL-02
   true-division rule and emitting `float_truediv_op (a b: int) : real`.
   Also landed here: the TYPING half of #30's capability 11 (an f-string in a function
   DECLARED `-> str` is string-typed in `_is_string_expr`, not only in the lowering).
3. **EVERY-RHS-STRING-TYPED local, as a FIXPOINT.** `_collect_string_literal_locals` marked
   a local `string` only when every assignment RHS was a plain `String` LITERAL. Generalised
   to `_is_string_expr`, iterated (marking one local makes another's RHS string-typed).
   Conservative in the same way: any non-string RHS anywhere excludes the local.
4. **STRING SUBSCRIPT.** `s[i]` on a string receiver is a one-character string
   (`str_sub_op s i 1`, the same op and law the `for c in <str>` element read already used).
   Fail-closed on a negative literal index.
5. **The `os.path` string model**, split by DETERMINISM, which is all that is claimed:
   `basename`/`dirname`/`normpath`/`relpath`/`join` are `val function`; `abspath`/`realpath`/
   `expanduser` read cwd/`$HOME` so they are plain `val` (equal arguments need not agree);
   `exists`/`isfile`/`isdir`/`islink`/`isabs` are filesystem predicates -> `int`. Plus a
   SLOT recognizer at the subscript for `os.path.splitext(p)[k]` / `split` / `splitdrive`
   (only a LITERAL 0/1 index).

## A FALSE `CLEAN` THE SIGNATURE REPAIR EXPOSED — and the marker that now catches it
With the mirror signature preserved, `proof2why3.from_sexp._find_construct_idx` scored
CLEAN. Its emitted body: `any_1 (Array.make 1 0)` — `any(<genexpr>)` has no lowering, so
the whole generator and every variable it reads are replaced by a FRESH CONSTANT ARRAY. It
also lowers `return None` to `raise (Return 0)`, conflating "not found" with index 0.
NOT CONVERTED. New probe marker: an ARITY-SUFFIXED abstract op applied to `(Array.make n 0)`
— keyed so the legitimate `let a = (Array.make 1024 0) in` initialiser is untouched.

## THE FRAME FIXPOINT — a boundary found and broken in the same window

Why3 REJECTS an OVER-claimed `writes` ("this write effect does not happen in the
expression"). A converted method whose live body writes emitter state ONLY THROUGH a
`\trusted` cross-mixin protocol stub therefore could not state its honest frame: the stub's
`val` declared no writes, so the converted body wrote nothing in the MODEL while its
`#@ assigns` — correctly derived from the LIVE transitive closure — listed seventeen fields.
Measured on `statements._emit_array_local_reassign`, otherwise CLEAN.

Narrowing the CALLER to `#@ assigns \nothing` also makes it CLEAN — measured — and was
REFUSED: `assigns` is an upper bound on effects, so UNDER-claiming is the direction that
misleads a caller, and it would move an existing dishonesty out of the counted trusted-63
and into the converted population.

THE FIX went the other way. `StatementEmissionMixin._expr_to_whyml` /
`ControlFlowStmtMixin._expr_to_whyml` are cross-mixin PROTOCOL STUBS (`return ""`, no live
counterpart in that file) and carried NO `#@ assigns` clause at all — an IMPLICIT
`writes {}`, which is false. They now declare the frame. Every converted caller then has to
list it EXACTLY (Why3 rejects both directions), so this is a FIXPOINT — and relaunch #19
already built the device: drive `#@ assigns` against Why3's OWN ERROR TEXT as a LOOP rather
than an analysis. `scratchpad/w4/framefix_loop.py` does it; it **converged in ONE iteration
per file** across `statements.py` (6 callers), `stmt_control_flow.py` (1) and
`expressions.py` (3). Corpus byte-diff 0.

**MEASURED AND NOT LANDED:** doing the same for the OTHER TWELVE no-`#@ assigns` protocol
stubs converges too (2 more iterations) and yields **ZERO** additional conversions — an
honesty-only change at the price of three whole-file re-proofs, and the field set must then
be DERIVED PER STUB rather than the blanket 17 used for the spike.

## WHERE THE LADDER STANDS

0. **The FOURTEEN `\trusted` stubs with NO `#@ assigns` clause** — an implicit `writes {}`
   the frame-honesty counter cannot see (it counts stubs that declare `\nothing`
   explicitly). Twelve are cross-mixin protocol stubs. Method: the same fixpoint loop.
   Priced above: honesty-only, 0 markers, 3 re-proofs, per-stub derived frames.
1. **Repair the 16 mirror-signature drifts** (gate above). The 10 MISSING-parameter stubs
   are a live fidelity hole — `_handle_dotted_call`'s trusted interface is for a function
   that has not existed since #29. Each repair changes that mirror's emission and costs a
   whole-file re-proof. The 6 renames are measured to buy measurement only.
1b. **`<x> or []` IS A WRONG LOWERING, and it is the LARGEST identified family in the tree:
   54 `\trusted` stubs.** Python's `or` returns a VALUE; the emitter lowers it as a BOOLEAN.
   `for ens in (rec.get("ensures") or []):` emits
   `iter_length (if (rec_get_2 … <> 0) || ((Array.make 1024 0) <> 0) then 1 else 0)` — a
   `1` or `0` where a list belongs. The correct rule is
   `A or D` => `(if <truthy A> then A else D)` in a VALUE position, gated on a type
   agreement the emitter can DECIDE (both string / both array / both emit_ir) and failing
   closed to the boolean form otherwise. `_handle_binop` ALREADY carries a CLOSED-KEY
   special case of exactly this (`<emit_ir>.get(k) or []` for the seven node-list keys), so
   the emit_ir slice is already covered and the residue is the DICT slice, where `or []`
   has to be read as EVIDENCE that the map's value type is a list — i.e. it meets backlog
   item 1b-B (empty-collection-literal value-type inference). MEASURE THE CORPUS BYTE-DIFF
   FIRST: this touches a general operator, and a corpus `x or []` in a BOOLEAN position
   must stay byte-identical.
2. **The `int` <-> `string` boundary is still the biggest family** — 51 `int`-into-`string`
   and 30 `string`-into-`int` on the REPAIRED census. This window took five bites out of it
   (re, Path, os.path, string subscript, string locals) for 8 markers; the residue is
   dominated by opaque `\trusted`-callee returns and heterogeneous `Dict[str, Any]` reads.
3. **The heterogeneous `Dict[str, Any]` parameter.** ~13 emitter-mixin stubs whose first
   blocker is `match Map.get <ir> "type" ... None -> 0` compared with `str_eq_op`. The
   device that fixes it EXISTS and is used exactly twice: a closed-key `TypedDict` VIEW in
   the mirror (`ValIRBoolView`), which monomorphizes to a WhyML record. Untried at scale.
4. **The recursive node ADT / structural measure** — unchanged, still the reopening
   capability for `traverse`'s 88 shadowed call sites and `visit_If`.
5. `interleave` monomorphisation, `option string` record-field reads — unchanged from #30.

## A POSSIBLE BLIND SPOT IN `check-trusted-frame-honesty` (recorded, not acted on)
`ConcurrencyChecker._walk_body` was converted with `#@ assigns \nothing`. Live, it calls
`_walk_stmt` -> `_warn_if_unprotected` -> `self.warnings.append(...)`. The gate's transitive
closure follows DECLARED frames and `_walk_stmt`'s trusted stub declares `\nothing`, so the
write is invisible — and `_warn_if_unprotected` itself is not in the gate's 63 either. Two
readings: the closure stopping at a declared frame is by design (the falseness is counted at
the stub that declares it), or `<list-field>.append` is not recognised as a self-write.
**Check which, before trusting the 63.**

## THE DEFINITIVE RANKED CENSUS AT WINDOW END (repaired probe, all #31 capabilities)
Every census taken BEFORE the signature repair is unreliable; this is the first honest one.

    39  int -> string        28  int -> array        15  string -> int
    14  int -> emit_ir       10  () -> int            9  int -> map ('mu -> option int)
     8  array int -> int      7  array string -> int  5  syntax error / 5 py_classdef_node
     4  tuple pattern         4  ref 'mu @rho         4  PARAM-LIST DIVERGES

**`int` vs `emit_ir` (14) LOOKS cheapest and is NOT uniform** — SPIKED: `pure_ast._Parser.node`
needs a `**kw` dynamic-construction model, not an annotation (`_fin` gaining a truthful
`-> "ExprIR"` was measured byte-safe and did not move it). Check each member individually.
The family: `statements._handle_assign_stmt` `._typed_local_vars` · `expressions._e`
`._to_bool` `._match_pattern_cond` `._handle_sum_call` `._content_string_method` ·
`Module5_IREmitter._get_mutex_invariant_ir` `._csl_in` `._csl_list_to_ir` `._py_expr_fstring`
`._py_stmts_to_ir` `._normalize_union_annotation` · `Module3_Weaver._desugar_acts` ·
`pure_ast._Parser.node`.

## INSTRUMENT FACTS #31 ADDS
1. `scratchpad/w4/port_sig.py` — the SIGNATURE-PRESERVING port, matching the repaired probe.
   Use it, not the older `port*.py`, for any stub whose mirror signature is refined.
2. **Match the `#@ \trusted` marker ANCHORED (`^#@\s*\\trusted\b`).** A loose
   `"\trusted" in line` test also matches a PROSE comment that mentions the directive — the
   mirror has several — and then deletes the wrong line while leaving the marker in place,
   so the "conversion" silently does nothing. Cost: one wasted cycle on `_err`.
3. **Resolve an emitted WhyML name by `<class>__<method>`, never by a suffix match.**
   `_Unparser.block` matches `_fin_block` under `endswith("_block")`, and a gate that
   misidentifies its subject issues a clean bill of health.
4. `scratchpad/w4/diag_any.py <mirror-relpath> <Class:name>` prints the WhyML around the
   first type error and restores the tree. NOTE: it still ports the LIVE header — use the
   probe for a verdict, this only for reading the emitted text.
