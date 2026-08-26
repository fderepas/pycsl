# Independent review: `csl-dispatch-expansion.md`

Reviewer: independent (no access to the author's transcript). Date: 2026-08-26.
Reviewed at the report's own HEAD, commit `3b435674` (worktree detached there; it is a
descendant of `eaaf85f7`). Every oracle below was run by me, foreground, in this worktree.

**Environment caveat (declared up front):** my why3 roster is Alt-Ergo **2.6.3** + Z3 4.13.3
(the loop's canonical `Alt-Ergo,2.6.2,` is not installed here — the pycsl default prover string
does not resolve, and I re-ran with `--provers "Alt-Ergo,2.6.3,,Z3,4.13.3,"` semantics by driving
`why3 prove` directly with the same `-a split_vc -t` options pycsl uses). Z3 matches the canonical
version exactly. All verdicts below carry that caveat.

---

## Headline verdict: **MIXED — spike should PROCEED, but amended**

The report's *central falsifiable claim* (§7.2: the VIEW device is a synthetic `_type` tag test
on an opaque pyval, needing **no new certificate and no new axiom**) is **CONFIRMED from emitted
WhyML**. The constness premise (§3) is **CONFIRMED exactly**. The whole-file baseline is
**CONFIRMED at 0 non-Valid** (927/927 goals, dual-prover merge). But two claims are **REFUTED in
part**, and both change the build plan:

1. **§3/§7.2's "same shape" claim hides a missing capability.** The tag-test *lowering* exists,
   but the 26-entry **table data never reaches the IR** that recognizers consume — Module 5 drops
   class-level `Dict[type, str]` tables entirely. A faithful conversion needs a table-reflection
   channel that does not exist today. "It is an emitter recognizer" is an under-estimate: it is an
   emitter recognizer **plus a Module 5 class-constant collection extension** (or an explicitly
   gated alternative — see R1 below).
2. **§4's "74 of 75 handlers already verified" is wrong: it is 72 of 75.** Two handlers
   (`_csl_subscript_field`, `_csl_nested_subscript`) are absent from the mirror altogether, and
   the mirror's own `_CSL_HANDLERS` table is stale by the same two entries — a fidelity drift the
   sync checker cannot see (it compares un-trusted *bodies*; the table is not a function).

Neither refutation kills the lever. Both must be priced in before the spike is meaningful.

---

## Per-question findings, with oracle artifacts

### Q1 (§7.2, the decisive one): CONFIRMED mechanism, REFUTED "nothing else needed"

**What `isinstance(n, _ast.Cls)` actually lowers to — from emitted WhyML, not comments.**
I ran:

```
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/monomorphize.py \
    --import-path src/pycsl --no-proof --keep-mlw
→ [+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks [L3-tc ✓]...)
```

and inspected `src/self-annotate/src/frontend/monomorphize.mlw`, which contains (verbatim):

```
  let _extract_ast_subscript (node: pyval) (generic_names: map string bool) : option (string, string)
    requires { true } ensures { true }
  = match node with
    | PDict d ->
        (match pget_dyn "_type" d with
         | Some (PStr t0) -> if pystr_eq t0 "Subscript" then
             (match pget_dyn "value" d with
              | Some (PDict vd) -> ...
```

So yes: `isinstance` is a **`pystr_eq` tag test on a synthetic `_type` key of an opaque `PDict`
pyval**, with a trivial `requires {true} ensures {true}` contract — *not* a match on the certified
`pyast_stmt` ADT. The emitter template (`emit_extract_ast_subscript_group`,
`src/pycsl/module6_whyml/generic_fold.py:12910` area) says so itself: *"NO new type/axiom/cert,
ledger 3"*. Report §7.2's central claim stands. A bonus in the report's favor: a tag *equality*
test is actually a **more exact** model of `type(op)` (exact class) than of `isinstance`
(subclass-closed), so dict-key use fits the device *better* than isinstance does semantically.

**But dict-key use differs in one load-bearing way: where the class-name literals live.** The
banked recognizers are all *name-gated per function* and **reflect their kind literals from the
function's body IR** (`recognize_extract_ast_subscript` walks `func["body"]` and extracts
`cls0/cls1/cls2`). For `_py_op_to_str` the mapping lives in a **class-level table**, and I
verified the table does not survive into IR at all. Oracle (Modules 1–3–5 driven directly on the
mirror `Module5_IREmitter.py`, IR dumped to JSON):

```
$ grep -c "PY_OP_MAP\|CSL_HANDLERS\|PY_EXPR_HANDLERS\|PY_STMT_HANDLERS" mirror_m5_ir.json
0            # in 672 KB of IR for the whole mirror file
```

`type_decls` for the class carries only typed fields (int constants come through
`_collect_class_constants`, string-set constants through `_collect_class_str_set_constants` —
`src/pycsl/frontend/Module5_IREmitter.py:2955` and `:2982`). **There is no `Dict[type, str]`
collector.** A recognizer therefore has *nothing to reflect the 26 mappings from*.

**And the probe of what happens today** — I ran full pycsl on a minimal file with the exact live
body (`return self._PY_OP_MAP.get(type(op), "?")`, un-trusted):

```
$ PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py scratchpad_probe_dispatch.py --import-path src/pycsl --keep-mlw
...
File "scratchpad_probe_dispatch.mlw", line 17, characters 4-52:
This expression has type int, but is expected to have type string
[-] Verification FAILED or INCOMPLETE.
```

with the generic lowering being literally:

```
    (self__PY_OP_MAP_get_2 (py_type_1 op) 365291336)
```

— opaque vals for `.get` and `type()`, and the `"?"` default **int-hashed to 365291336**. Two
consequences: (a) the current pipeline fails *loudly* on this shape (fail-closed, no accidental
facade — good); (b) any conversion must be a bespoke recognizer, exactly as the report says.

**Judgment:** `type(op)`-as-dict-key CAN reach the same tag-test lowering, with no new
certificate and no new axiom — *the report is right about the capability class*. But the faithful
route requires one of:

- **(i)** a new Module 5 collector for class-level `Dict[type, str]` tables (the
  `_collect_class_str_set_constants` precedent — whose own docstring states the exact faithfulness
  rationale: lower over "the ACTUAL members …, not an int-hash of the set's NAME (a facade that is
  invariant under the set's contents)"). This is a live-compiler change: corpus byte-diff gate,
  plus mirror-sync cost (a new live function must appear in the mirror — as a new trusted stub it
  *raises* the count it is trying to lower unless converted in the same window).
- **(ii)** hard-coding the 26 entries in the emit template. **This should be rejected**: with
  `ensures {true}` contracts, a wrong hard-coded mapping proves just as well as a right one, and
  the report's own Gate C (non-vacuity: "must really tag-test and really call the handlers")
  cannot see a wrong *mapping*, only a missing *test*. This would be silent unfaithfulness of
  precisely the class the str-set collector was built to prevent.
- **(iii)** refactoring the live `_py_op_to_str` into an explicit isinstance/elif chain so the
  literals reflect from body IR like every banked device. Behavior-identical, byte-diff-0 by
  construction — but it changes the live compiler and abandons "constant-table expansion" as the
  advertised shape.

**Amendment to Gate S:** the spike must *choose and name* its table-reflection route before it can
be judged, and if (i) is chosen, the mirror-side accounting of the new collector must be part of
the spike's cost. §7.2's "no new certificate" survives; "needs NO new [anything]" does not.

### Q2 (§3 constness): CONFIRMED exactly

AST-level oracle over `src/pycsl/frontend/Module5_IREmitter.py` at HEAD:

```
_CSL_HANDLERS      entries: 79  keys all Name/Attr: True  values all str const: True  distinct values: 75
_PY_EXPR_HANDLERS  entries: 23  keys all Name/Attr: True  values all str const: True  distinct values: 23
_PY_STMT_HANDLERS  entries: 16  keys all Name/Attr: True  values all str const: True  distinct values: 16
_PY_OP_MAP         entries: 26  keys all Name/Attr: True  values all str const: True  distinct values: 22
```

All four match the report's table (79/26/23/16). A tree-wide grep for `TABLE[`, `.update(`,
`.pop(`, `.setdefault(`, and any reassignment of the four names over `src/` (mirror excluded)
returned **zero hits**. The finite-case-split premise is sound. (Table locations:
`Module5_IREmitter.py:522`, `:1081`, `:1313`, `:1333`.)

### Q3 (§4 payoff): PARTLY REFUTED — 72/75, not 74/75

Script over the mirror (`\trusted` marker → next `def`) crossed with the live `_CSL_HANDLERS`
values:

```
distinct handlers: 75
missing from mirror: ['_csl_nested_subscript', '_csl_subscript_field']
trusted handlers: ['_csl_in']
dispatchers trusted?: {'_py_op_to_str': True, '_csl_to_ir': True, '_py_expr_to_ir': True, '_py_stmts_to_ir': True}
```

`_csl_in` as the sole trusted *present* handler: confirmed. But `_csl_subscript_field`
(live `:718`) and `_csl_nested_subscript` (live `:748`) **do not exist in the mirror at all**, and
the mirror's own `_CSL_HANDLERS` literal is missing the same two entries
(live-only keys: `NestedSubscript`, `SubscriptFieldAccess`; mirror table has 77 entries vs live
79). The sync checker (`bin/check-self-annotate-mirror-sync.py`) does not flag this — it
compares un-trusted mirror *bodies*, and neither a missing method nor a stale class-level table is
a body. An expanded 79-way `_csl_to_ir` would call two methods the mirror does not define. The
"79-way" build therefore has a **pre-step the report does not price**: sync the table + add the
two handlers (two new conversions, or two new trusted stubs, i.e. a temporary +2).

### Q4 (baseline): CONFIRMED — 0 non-Valid at HEAD, 927 goals (with prover caveat)

This was the expensive run, done foreground in three stages because a single dual-prover pycsl
invocation exceeds my 600 s per-command cap (the one run that hit the cap was killed immediately;
see process confirmation at the end):

1. **Full-file, Z3 only, t=30** via
   `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/Module5_IREmitter.py --import-path src/pycsl`
   (canonical `Alt-Ergo,2.6.2,` absent from my why3.conf, so only the Z3 leg ran):
   `[-] 5 goal(s) remain unproven after all provers` — all five `Timeout (30.00s, ...)`.
   So **Z3 alone does NOT prove the file** — the dual-prover merge is load-bearing.
2. **Full-file, Alt-Ergo 2.6.3, t=5**, driving why3 exactly as pycsl does
   (`why3 prove -a split_vc -P "Alt-Ergo,2.6.3," -t 5 --json <mlw>`, 10m14s):
   `total goals: 927; Counter({'Valid': 876, 'Timeout': 51})`. The 51 are the size/variant lemma
   pack (`size_*_dec`, `size'vc`, `wf_ir_binds'vc`, `is_*_faithful`, the `_scan_2d_in_expr`
   sub-lets…).
3. **The 51 AE-timeout sub-goals re-attacked with Z3 at t=30** (`-g <file>:<line>` selectors,
   25 s total): `total goals: 51; Counter({'Valid': 51})`.

Every goal is Valid under at least one of the two provers at t=30 ⇒ **merged whole-file baseline
= 0 non-Valid out of 927**, under AE 2.6.3 + Z3 4.13.3. Since any true non-Valid set must be a
subset of the AE-timeout set, stage 3 closes it completely. The report's precondition holds.
(The 5 Z3-only failures are AE-fast goals; conversely the 51 AE-t5 stragglers are Z3-fast — this
file *needs* both provers, which the spike's gate battery should keep in mind before blaming any
future regression on the expansion itself.) Fidelity baseline also re-measured:
`bin/check-self-annotate-mirror-sync.py` reports exactly **2 DIVERGED**
(`module6_whyml/expressions.py::_handle_var_expr`, `module6_whyml/stmt_control_flow.py::_handle_for_stmt`)
— matching the report's "2 DIVERGED" baseline.

### Q5 (§5 mutual recursion): CONFIRMED, and the risk is slightly *wider* than stated

From the emitted mirror WhyML (same `--no-proof --keep-mlw` artifact,
`src/self-annotate/src/frontend/Module5_IREmitter.mlw`):

- `_csl_to_ir` is opaque today — and not once but as a **family of val avatars**:
  `val function csl_to_ir` (line 710), `val function csl_to_ir_op` (877),
  `val function emit_ir_disp__csl_to_ir` (1318), plus per-handler `self__csl_to_ir_1` aliases.
- Handlers are *program* `let`s calling those vals, e.g. (verbatim):
  ```
  let pycsltojsonemitter___csl_binop (self: pycsltojsonemitter) (node: cslbinop) : emit_ir
    requires { true } ensures { true } writes { }
  = (IrBinOp node.cslbinop_op (self__csl_to_ir_1 node.cslbinop_left) (self__csl_to_ir_1 node.cslbinop_right))
  ```

So yes: the back-edge is an opaque total `val function` with **no termination obligation**, and a
real `_csl_to_ir` body dispatching to the handlers closes a genuine mutual-recursion cycle needing
`let rec … with` + variants across the cluster. Two things the report under-states:

- **The variant infrastructure already exists** — `let rec function size (e: emit_ir)` (mlw line
  344) and the `size_*_dec` lemma pack were built precisely as a size measure for recursive
  consumers of `emit_ir` (they are 23 of my 51 AE-t5 stragglers, all Z3-fast). The risk is real
  but not greenfield.
- **A shell-game hazard the gates must name:** a "conversion" that defines a program `_csl_to_ir`
  dispatching to the handlers while the handlers keep calling the *opaque val avatars* removes the
  `\trusted` marker without discharging the totality assumption — the val family stays axiomatic
  and nothing ties it to the new program function. Gate C as written ("really calls the handlers")
  does not exclude this. The gate should require the **back-edge itself** be the recursive
  program function (all avatars retired or proven equal), or the conversion is vacuous.

Also note `_csl_to_ir`'s mirror param is retyped `"ExprIR"` (the certified `emit_ir` ADT), *not*
pyval — so §7.2's pyval-VIEW argument, which is the right story for `_py_op_to_str` /
`_py_expr_to_ir` / `_py_stmts_to_ir` (raw-ast inputs), is **not** the device `_csl_to_ir` will
use; that one dispatches over the certified ADT (the `isinstance`-on-CSL-class → `is_fieldget`
recognizer precedent at mlw line 184). Two different devices for the four targets; the report
blurs them into one.

### Freshness (§7.4): CONFIRMED

All four targets are `#@ \trusted` with placeholder bodies at HEAD `3b435674`:
`_csl_to_ir` → `return {}` (mirror line 73), `_py_op_to_str` → `return ""` (708),
`_py_expr_to_ir` → `return {}` (722), `_py_stmts_to_ir` → `return []` (1107). This wall is not
stale.

---

## What the spike plan should change

1. **Gate S gains a precondition:** name the table-reflection route (recommend (i): a
   `Dict[type, str]` class-constant collector following `_collect_class_str_set_constants`,
   entries reflected — never hard-coded in the template), and count its mirror-sync cost in the
   spike's yield. Reject route (ii) explicitly in the gate text.
2. **Non-vacuity for `_py_op_to_str` must check the mapping, not just the tag-testing:** all 26
   reflected pairs present in the emitted match, byte-compared against the live table (Gate C as
   written would pass a wrong mapping).
3. **Before any `_csl_to_ir` work:** sync the mirror's stale `_CSL_HANDLERS` (+2 entries) and add
   the two missing handlers; fix the §4 count to 72/75 in the plan of record.
4. **`_csl_to_ir`'s gate must require the recursive back-edge be the defined program function**
   (no surviving opaque `csl_to_ir*` val avatars), or the marker removal is a shell game.
5. Keep the dual-prover battery for the whole-file gate — this file is only 0-non-Valid under the
   *merge* (Z3 alone: 5 timeouts; AE-t5 alone: 51).

## Process confirmation

All commands ran in my own turns. One dual-prover pycsl run exceeded the 600 s per-command cap
(my Bash tool's hard maximum — the suggested 1800000 ms is not acceptable to it) and was
auto-parked; I stopped it immediately with TaskStop before proceeding, and re-did the work in
capped stages. Final check before returning:

```
$ ps -eo pid,ppid,etimes,cmd | grep -E 'pycsl.py|why3|alt-ergo|sertop' | grep -v grep
(no output — nothing of mine survives)
```

(An earlier run of this check caught a concurrent `pycsl.py … Module2_Parser.py --provers
Alt-Ergo,2.6.3,…` process tree under `timeout 1800` — a file and an invocation I never ran; that
is the main-checkout agent's work and was left strictly alone. The final check above is clean.)

Worktree side effects: regenerated `.mlw` files under `src/self-annotate/src/frontend/` and a
temporary probe (`scratchpad_probe_dispatch.py/.mlw`) were deleted after use; nothing committed,
nothing pushed.
