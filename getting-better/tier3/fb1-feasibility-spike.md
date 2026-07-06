# F-B1 — faithful `Dict[str,Any]` value-model — Phase-0 STOP-gate feasibility spike

**VERDICT: NO-GO.** F-B1 is **not feasible as a bounded Tier-5 build.** The WhyML
`pyval` value type itself is sound and cheap (S1 green, axiom-free), and its
Rocq/Lean certificate would be a conservative axiom-free side-car (S2 feasible)
— **but the decisive test (S1b) fails: two REAL V1 generic-dict walkers, ported
verbatim, do NOT whole-body-prove.** They are rejected/errored at the *emitter /
lowering* layer for two independent blockers that a faithful value type does
**not** address. The census's "V1 leave-trusted / F-B1 is unbounded" conclusion
is **vindicated**; the value-first STOP stands.

Branch `ghost-assign-bc6`, baseline HEAD `af005a55`, count **1240** (held —
every real-stub probe reverted, mirror clean). Provers: system Alt-Ergo 2.6.2 +
Z3 4.13.3 under Why3 1.8.2. Spike env: project `.venv` (libcst present; sync
verified to replace real bodies + LIVE signatures — see S1b assertion).

---

## S1 — the WhyML `pyval` spike: **PASS** (green, axiom-free)

File: `test-suite/corpus/conformance/spikes/fb1_pyval_spike.mlw` (two modules).

```
type pyval = PInt int | PStr string | PBool bool | PNone
           | PList (list pyval) | PDict (list (string, pyval))
```

- **Type-checks:** PURE (no mutable field; `list`, never `array`). The nested
  inductive through `list (string, pyval)` is accepted by Why3.
- **Mutual structural recursion / termination — ACCEPTED.** `size` /`size_list`
  /`size_pairs` and the generic `.values()`-style walk `str_leaves` /
  `str_leaves_list` /`str_leaves_pairs` are pure logic `function`s; Why3's
  **syntactic structural-termination checker accepts them** (no `Admitted`, no
  axiom). Termination of the heterogeneous-tree walk is sound.
- **Toy laws — all 14 positive goals Valid best-of-N (union of Alt-Ergo + Z3):**
  discriminant/dispatch (`g1_*`, 4), key read-back
  `pdict_get (PDict [("a",PInt 1)]) "a" = Some (PInt 1)` (`g2_read_hit`),
  guarded miss (`g2_read_miss_guarded`), recursion laws (`g3_dict_law`,
  `g3_list_law`, `g3_nested`), the generic-walk collect + membership laws
  (`g4_collect_hit/nested/none`), and the map-form reads (`gm_read_hit`,
  `gm_read_default`).
- **All 4 false twins stay UNPROVEN on BOTH provers** (`g2_false_twin`,
  `g3_false_twin`, `g4_false_twin`, `gm_false_twin` → Timeout on Alt-Ergo and
  Z3). Correct.
- **No `axiom` keyword** in the file.

### Two FRICTION FINDINGS surfaced inside S1 — the seeds of the S1b NO-GO

These are *green in the file* (documented/guarded), but they are precisely the
operations every real generic-dict emitter stub performs, and they do **not**
discharge in the naive form:

1. **String-keyed dispatch does not SMT-discharge under the recursive read.**
   A first-key hit needs only reflexivity (Valid, Alt-Ergo). But a *miss* or a
   *second-key* read forces `assoc_get`'s `else` branch, which needs a string
   **disequality** (`"z" <> "a"`) to fire *under the recursive definitional
   unfold*. The **bare** goal
   `pdict_get (PDict [("a",PInt 1)]) "z" = None`
   **TIMES OUT on BOTH provers (10 s)** — even though `("z"="a") = False` is
   Valid on Z3 in **0.01 s** standalone. It goes green ONLY when the
   disequality is fed as a hypothesis (`g2_read_miss_guarded`, Valid Alt-Ergo)
   or via an explicit unfold `assert`-chain. This is the exact
   `stmt.get("type") == "Return"` move every emitter dispatch makes — kept in
   the file as `g2_read_miss_bare_FRICTION_WITNESS` (deliberately unproven,
   like a false twin).

2. **The explicit-`variant` termination VC for the pair-nested walk does not
   SMT-discharge.** The `let rec function size ... variant { v/l }` PROGRAM form
   of the same functions is accepted by Why3, but its generated
   `size_pairs'vc` decrease obligation **TIMES OUT on BOTH Alt-Ergo and Z3**:
   the well-founded-order VC for the *doubly-nested* subterm `v` in
   `Cons (_, v) t` (list → pair → pyval) is not SMT-dischargeable, whereas the
   *singly-nested* `size_list` (`Cons h t -> size h`) VC IS Valid. Termination
   is sound only via the syntactic checker (pure logic `function`), not via the
   explicit-variant SMT route the emitter would generate for a program walk.

### S1a vs S1b module contrast (the map form)
`PDict` as `list (string, pyval)` (module `PyValListDict`) admits both key
read-back AND a terminating generic `.values()` walk. `PDict` as
`map string pyval` (module `PyValMapDict`) admits key read-back (total
`Map.get`, but that models dict-**with-default**, NOT faithful `KeyError`), and
has **NO structural `size`/`.values()` walk at all** — a total map is not an
inductive with finitely many children. So the *only* walkable faithful form is
the association-list one, which is exactly the form that incurs friction #1/#2.

---

## S1b — THE DECISIVE TEST: port REAL V1 stubs and whole-body full-prove — **NO (both fail)**

Method (census §10.1): `git`-clean mirror → drop the ONE `\trusted` line of the
target → `bin/sync-mirror-bodies.py module6_whyml/ir_scanner.py` (ports LIVE
params+body+returns; **asserted the LIVE signature replaced the stub**, not the
libcst-absent artifact) → `PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <mirror>
--import-path src/pycsl --fun <qual>` → revert. Both probes reverted; count 1240.

### Probe 1 — `IRScanner.find_named_expr_targets` (the canonical generic walker)

LIVE body (signature asserted ported: `(obj: Any, targets: Set[str]) -> None`):
```python
if isinstance(obj, dict):
    if obj.get("type") == "NamedExpr":
        targets.add(obj["target"])          # by-ref Set[str] param mutation
    for k, v in obj.items():                # generic .items() over Dict[str,Any]
        if k == "stmt": continue
        IRScanner.find_named_expr_targets(v, targets)   # recurse over Any
elif isinstance(obj, list):
    for item in obj:
        IRScanner.find_named_expr_targets(item, targets)
```
Hits **all three** known-hard sub-problems: (a) `.get("type")` string dispatch,
(b) by-ref `Set[str]` param mutation, (c) generic `.items()` heterogeneous
recursion over `Any`.

**RESULT: REJECTED at the emitter — never reaches proof.** Verbatim:
> `[module6-whyml]: in-place mutation of dict/set parameter 'targets'
> (`targets.add(...)`) is out of scope: … a faithful model requires a
> caller-visible mutation frame (`writes {targets}`) that PyCSL's by-value map
> parameter does not provide (the SAME boundary as record-param and nested-list
> inner mutation). Rework … to RETURN the updated collection, or mutate a LOCAL
> copy …`

**Exact blocker: (b) by-ref `Set`/`Dict` parameter mutation — the WL-05
rejection class, a frame/aliasing boundary.** This is **orthogonal to value
typing**: a faithful `pyval` does NOT fix it — the block is about caller-visible
mutation of a by-value map parameter, not about the value's element type. So
even a fully-built F-B1 value model would leave this stub (and every
by-ref-mutating generic walker) rejected.

### Probe 2 — `IRScanner.find_return_type` (a READ-ONLY generic-dict walker)

Chosen to *isolate* blockers (a)+(c)+string-emission, with NO param mutation:
`(stmts: List[Dict[str, Any]]) -> str` reading `stmt["stmt"]`,
`stmt.get("stmt") == "Match"`, `val.get("type") == "Tuple"`, recursing through
`stmt["body"]/["orelse"]`, and building a return-type **string**.

**RESULT: lowers further, then WhyML TYPECHECK ERROR — does NOT prove.** Verbatim:
> `File "…mlw", line 112: This expression has type array.Array.array int @rho,
> but is expected to have type int`  →  `Verification FAILED or INCOMPLETE.`

**Exact blocker: (a)+(c) manifest as the B1 opaque-dict value-collapse type
wall** — the `Dict[str,Any]` values are modelled as `array int`, so a
string-keyed read where an `int` is expected produces an `array int` vs `int`
mismatch. This is the census's V1 `DICT-B1` ceiling itself. Note that, per S1
friction #1/#2, even if the value model *did* give these reads their real
types, the whole-body proof would then hit the string-dispatch and
heterogeneous-walk SMT frictions measured in S1.

### S1b verdict
**NO — a REAL V1 whole-body port does NOT full-prove.** Two representative
walkers, two independent blockers, neither reaching `Verification SUCCESS`:
- by-ref `Set`/`Dict` param mutation (WL-05 frame boundary) — **pyval does not
  address it**;
- opaque-dict value int-collapse (B1 type wall) + the S1-measured
  string-dispatch / walk-termination SMT frictions that survive the model.

This is exactly the census's whole-body lesson: a `pyval` that proves toy laws
but that a real generic-dict walker still can't lower/prove against is a NO-GO.

---

## S2 — certificate feasibility (sketch only; not integrated)

**Feasible and axiom-free — NOT the blocker.** `pyval` is a positive nested
inductive; Rocq/Coq accepts
`Inductive pyval := PInt Z | PStr string | PBool bool | PNone | PList (list
pyval) | PDict (list (string*pyval))` — the `Phase2b_RecordVal.v` `val7` shape
(`V7Rec (list (string*val7))`) extended with three leaf arms (`PStr/PBool/
PNone`) and a `PList` list-of-values arm. `size`/read-back/frame prove by
structural induction with **no axiom**; `Print Assumptions` (Rocq) / `#print
axioms` (Lean) would stay "closed under the global context" → the **3-axiom
ledger holds**. As with Phase2b, this is a **conservative side-car** (certifies
the value shape in isolation; does NOT integrate `pyval` into the core `val`
soundness induction) — sufficient for the §10.5 value-soundness obligation.

But the certificate is only meaningful once the emitter capability lands, and
S1b shows it **cannot** (rejection + type-collapse before any proof). So S2 does
not rescue the GO.

---

## Overall GO/NO-GO — **NO-GO**

| gate | result |
|---|---|
| `pyval` type-checks (pure, mutual recursion, termination accepted) | **PASS** (S1) |
| toy laws Valid best-of-N + false twins unproven + no axiom | **PASS** (S1, 14/14 + 4 twins) |
| **a REAL V1 whole-body port full-proves** | **FAIL (NO)** (S1b — both probes) |
| certificate conservative / axiom-free | PASS-feasible (S2), moot |

**GO requires all four; S1b fails.** F-B1 is confirmed **infeasible as a bounded
build**: the value type is fine, but the real generic-dict walkers are blocked
at the emitter by (b) by-ref param mutation (a frame boundary a value model does
not touch) and (a/c) the opaque-dict int-collapse type wall, and even a built
model would inherit the S1 string-dispatch + walk-termination SMT frictions.

**Recommendation: menu-D STOP for the V1 `Dict[str,Any]` cluster stands.** The
~85 V1 (+ ~40 V2-behind-façade) generic-dict readers remain **leave-trusted** on
the B1 semantic ceiling. F-B1 is not a Tier-5 feature; do not authorize the
model+certificate+convert build.

### Deliverables
- Verdict: this file.
- Spike: `test-suite/corpus/conformance/spikes/fb1_pyval_spike.mlw`
  (`git add -f`; `.mlw` is gitignored).
- No `src/` change: mirror reverted, count **1240**, tree = spike-doc + fixture.
