# wrong-lowering-to-fix.md — evidence-backed backlog of wrong / opaque / unsound lowerings

Deliverable of `finding-wrong-lowering.md`. Each finding below is backed by a committed,
re-runnable repro driver under `getting-better/wrong-lowering/` with a recorded verdict. NO
speculative entries. Ordered by severity (UNSOUND > FALSE-GREEN > COLLAPSED-with-consumer >
WRONG-REPR > COLLAPSED-no-consumer > OPAQUE).

Harness: `bin/find-wrong-lowering.py` (`run <f> [--no-proof]` → PROVEN/UNPROVEN/TYPEERR/VACUOUS;
`mlwtype <f>` → emitted WhyML signatures). Verify with
`PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <f>.py`.

**Verdict legend:** PROVEN = all VCs Valid; UNPROVEN = a VC can't be discharged; TYPEERR = emitted
WhyML fails Why3 type-check (fail-closed). For a *false-twin* driver, **PROVEN ⇒ UNSOUND**.

---

## D0 — calibration (passed)

Known-bad recall 4/4, known-good precision 6/6 (0 false positives). Set: `getting-better/wrong-lowering/calibration/`.

| driver | expected | verdict |
|---|---|---|
| cal_bool_faithful (bool=int, TRUE claim) | PROVEN | PROVEN ✓ |
| cal_bool_falsetwin (`==2`) | UNPROVEN | UNPROVEN ✓ |
| cal_dict_val_faithful (`map string (option int)` read-back) | PROVEN | PROVEN ✓ |
| cal_floordiv_pos_faithful (`(-7)//2==-4`, pos divisor AGREES) | PROVEN | PROVEN ✓ |
| cal_listlen_faithful (`len([10,20,30])==3`) | PROVEN | PROVEN ✓ |
| cal_listlen_falsetwin (`len==1024`, the backing size) | UNPROVEN | UNPROVEN ✓ |

The decisive false-positive guard is `cal_floordiv_pos_faithful`: a positive-divisor `//` PROVES, so
the WL-01 detector flags **only** the negative-divisor divergence, not all `//` — it does not
false-positive against the τ-blessed baseline.

---

## UNSOUND (severity 1) — proves a claim FALSE of real Python

### WL-01 — Python `//` / `%` on a negative divisor lowered to Why3 Euclidean `div`/`mod` — **FIXED**
- **Status:** ✅ **FIXED** (branch `ghost-assign-bc6`). `pycsl_div`/`pycsl_mod` now emit Python
  **floored** division/modulo: Euclidean `div`/`mod` corrected by a sign-of-**divisor** adjustment
  `if mod x y <> 0 && y < 0 then div x y - 1` (`+ y` for mod). The positive-divisor emission is
  byte-identical to Euclidean. The spec/contract side emits the same correction inline over the
  always-in-scope `div`/`mod` (operands `let`-bound once), so a body `a//b` and a contract
  `\result == a//b` denote the identical floored value.
- **Construct / position:** `BinOp //` and `BinOp %` in a function body OR contract, any divisor sign.
- **Faithful target realized:** Python is FLOORED division (`//` rounds toward −∞; `%` sign follows the
  divisor). Derivation is elementary; SMT discharges it — **no cited lemma needed**. Spike fixture:
  `test-suite/corpus/conformance/spikes/wl01_floored_divmod_spike.mlw` — all concrete make-or-break
  goals (`(-7)//(-2)=3`, `7%(-2)=-1`, `(-7)//2=-4`, `7//2=3`) Valid on **both** Alt-Ergo AND Z3; the
  general nonlinear identity `x = (x//y)*y + (x%y)` is Valid on Alt-Ergo (0.04s) and times out only on
  Z3 (known nonlinear-mult instability) — irrelevant to the drivers, which are concrete.
- **Class / severity:** UNSOUND / 1 (was).
- **Verdict flips (now):**
  - `getting-better/wrong-lowering/wl01_floordiv_neg_UNSOUND.py` → **UNPROVEN** (the false `==4` is no
    longer provable). Was PROVEN.
  - `wl01_floordiv_neg_TRUE.py` → **PROVEN** the TRUE `== 3`. Was UNPROVEN.
  - `wl01_mod_neg_UNSOUND.py` → **UNPROVEN** (false `==1` unprovable). Was PROVEN.
  - `calibration/cal_floordiv_pos_faithful.py` (`(-7)//2==-4`) → **STAYS PROVEN** (positive divisor
    unchanged).
- **Regression locks (reference corpus):** `test-suite/corpus/pycsl-reference/0811.py` (POSITIVE —
  proves `(-7)//(-2)==3`, `7%(-2)==-1`, positive-divisor coverage, and a symbolic-divisor
  `\result == a//b`) and `0812.py` (NEGATIVE, `# pycsl-expected: FAIL` — asserts the old false `==4`,
  now unprovable).
- **G1 correction:** translational-reference §T.11 G1's example `(-7)//2` was itself WRONG (Euclidean
  `div(-7,2)==-4` AGREES with Python). The true divergence is the negative *divisor*. G1 now marked
  RESOLVED with the corrected note.
- **Emission differential:** corpus byte-diff touches exactly the 33 div/mod-using reference programs
  (helper block + contract-side `//`/`%`); positive-only lowering unchanged in shape; corpus still
  proves.

### WL-02 — Python `/` (TRUE division, returns float) lowered to integer Euclidean `div` — **FIXED**
- **Status:** ✅ **FIXED** (branch `ghost-assign-bc6`). A Python TRUE-division `/` (IR BinOp op `"/"`)
  now lowers — in a body **and** in a contract — to a **real** division, NEVER the integer `pycsl_div`.
  Both int operands are lifted to `real` via `real.FromInt` (`from_int`) and divided over the reals
  with `real.RealInfix` (`/.`). Contract (`_in_spec`): `from_int a /. from_int b`. Body: bundled into
  one abstract `val float_truediv_op (a b: int) : real ensures { result = from_int a /. from_int b }`
  (`from_int` is a logic symbol, unusable in a program term). Because the result is a `real`, a `/`
  used at `int` type is a real-vs-int **type error** — fail-closed, never a silent integer truncation.
  FLOOR division `//` (IR op `"div"`) is UNCHANGED (WL-01 intact, stays integer floored). The
  `use real.RealInfix`/`use real.FromInt` imports are gated on `IRScanner.uses_true_division`, so a
  program with no `/` is byte-identical.
- **Real op / drivers:** `float_truediv_op` (`_handle_binop`, `module6_whyml/expressions.py`).
  `getting-better/wrong-lowering/wl02_truediv_UNSOUND.py` → **TYPEERR** (the false `5/2==2` at int type
  is a real-vs-int type error; was PROVEN). `getting-better/wrong-lowering/wl02_truediv_TRUE.py` →
  **PROVEN** the faithful `5 / 2 == 2.5` at `float` (real) type. SMT-feasibility spike (Alt-Ergo AND
  Z3, no cited lemma): `test-suite/corpus/conformance/spikes/wl02_truediv_real_spike.mlw`
  (`from_int 5 /. from_int 2 = 2.5`; the old `5/2 = 2.0` refuted; `from_int` operand-lift sound).
- **Class / severity:** UNSOUND / 1 (was).
- **Faithful target realized:** Python `a / b` is TRUE division → a `float` (`real`); the fractional
  part is preserved. Derivation is elementary real arithmetic; SMT discharges it directly — **no cited
  lemma needed**.
- **Regression locks (reference corpus):** `test-suite/corpus/pycsl-reference/0813.py` (POSITIVE —
  proves `5/2==2.5`, `1/2==0.5`, `7/2==3.5`, exact `4/2==2.0` all at `float`, PLUS a `//` guard that
  `5//2==2` stays integer) and `0814.py` (NEGATIVE, `# pycsl-expected: FAIL` — the old
  int-truncation `5/2==2`, now a real-vs-int type error).
- **Corpus programs that relied on the OLD unsound `/`:** 13 reference programs used `/` in a
  **contract** to mean integer division while the body used `//` (e.g. `0353` `#@ ensures \result ==
  256 / n` with body `256 // n`; `0004`/`0203`/`0209` Gauss-sum `n*(n±1)/2`). Under the old bug the
  contract `/` was Euclidean `div`, so they proved. These RELIED on the unsound `/`→int; they were
  reclassified by spelling the contract with `//` (the sound integer division that matches the body).
  All 13 still PROVE; their emission is byte-identical to the old (0353–0362,0365,0376,0381–0383,0391)
  or differs only by dropping a **dead** unused `pycsl_div` helper block (0004/0203/0209, contract-only
  division). Files: 0004,0203,0209,0353,0359,0361,0362,0365,0376,0381,0382,0383,0391.
- **Dedup:** none. Related mechanism to WL-01 (`pycsl_div`) but a distinct Python operator + fix.

---

## FALSE-GREEN / VACUOUS (severity 2)

### WL-VAC — nonlinear integer-division vacuity (cross-reference only; already documented)
- A module containing an integer-division-bearing function can destabilize Z3 into deriving `false`
  from a satisfiable context → a false `ensures` discharges (vacuous green). The default non-vacuity
  gate (`pycsl.py::_run_vacuity_gate`) CATCHES it.
- **Status:** DOCUMENTED — memory `vacuity_nonlinear_div.md`; investigation in
  `getting-better/csys-vacuity-investigation/`. The residual family is the dir-removal `dir_lookup`
  apparatus (os) + `csys yiq_to_rgb`. Pre-existing corpus fails `0540/0700/0701` are NOT findings.
- **Not re-reported here** (considered-and-excluded as an already-documented boundary). The D4 probe
  `scratch` `(a*b)//a` reproduces the Z3 division instability (times out rather than resolving),
  consistent with the documented root cause. Fix is tool-level (division encoding / prover config),
  tracked separately.

---

## COLLAPSED / WRONG-REPRESENTATION (severity 3–4)

### WL-03 — `Tuple[T1,…]` PARAMETER collapses to bare `int` (opaque `subscript_get`) — ✅ FIXED
- **Status:** FIXED (branch `ghost-assign-bc6`). A RECOGNIZED fixed-length `Tuple[T1, …, Tn]`
  PARAMETER **and** record FIELD now gets a synthesized per-slot record (reusing the NamedTuple
  positional-access seam), so `t[i]` reads the faithful slot type. Bare `tuple` and variable-length
  `Tuple[T, …]` (Ellipsis) are UNCHANGED (`int †` collapse).
- **Construct / position:** a `Tuple[...]`-annotated *parameter* (and field); slot read `t[i]`.
- **Was:** `let f (t: int) …` with `t[i]` → `val subscript_get (x:int)(i:int):int` (content-opaque);
  the faithful model was realized only for locally-constructed / returned tuples, NOT params/fields
  (a `Tuple[...]` field went `list`→`array int`).
- **Now:** Module5 `_synthesize_tuple_records` synthesizes one dedup'd record
  `type pytuple_<tags> = { field0: τ(T1); …; field{n-1}: τ(Tn) }` (`is_namedtuple: True`, int/bool→int,
  str→string); `_m5_get_type_name` (param) and `_field_type_from_annotation_inst` (field) resolve a
  recognized `Tuple` annotation to that record; `_param_type_str` emits the record param; the existing
  `_namedtuple_positional_access` lowers `t[i]` to `t.field{i}`. A record-PARAM field read (`b.p[1]`)
  is enabled by extending `_field_type_of` to consult `_record_param_classes`; the preamble record
  emitter emits a nested-record field type. **New scalars only** (float/container/class slot →
  unrecognized → unchanged collapse; record-field float is not modeled as `real`).
- **Faithful target (met):** per-slot record; `t[1] : string` for `Tuple[int,str]`, `t[0] : int`.
- **Class / severity:** COLLAPSED-with-consumer / 3 (mixed-slot: WRONG-REPR / 4).
- **Evidence (post-fix):**
  - `wl03_tuple_param_COLLAPSED.py` (`Tuple[int,str]`, `return t[1]`) → **PROVEN** (was TYPEERR).
  - all-int `Tuple[int,int]` param `t[0]` → content-**PROVEN** (was opaque/UNPROVABLE).
  - Baseline `wl03_tuple_local_FAITHFUL.py` (LOCAL tuple `t[1]==20`) → **PROVEN** (unchanged).
  - Reference locks: `0815.py` (POSITIVE — mixed + homogeneous param slot reads), `0816.py`
    (NEGATIVE twin, `# pycsl-expected: FAIL` — a false slot-content conflation, must stay UNPROVEN).
  - SMT spike: `test-suite/corpus/conformance/spikes/wl03_tuple_param_slot_spike.mlw` — per-slot
    record read of a mixed-type tuple PARAM, all goals Valid on Alt-Ergo AND Z3.
  - Emission-differential: the full 695-file `pycsl-reference` corpus emits BYTE-IDENTICALLY (no
    corpus program uses a recognized `Tuple[…]` param/field → additive).
- **Deliberate-collapse check:** N/A (fixed). The τ-table row is now `τ(Tuple[T1, …, Tn]) = record`.
- **Dedup:** none in we-are-getting-better.md.

### WL-04 — `List[T]` with a faithful non-int element (`List[str]`, `List[float]`) — element read collapses to `int` — ✅ FIXED
- **Status:** ✅ **FIXED** (branch `ghost-assign-bc6`). A FLAT `List[str]`/`List[float]` PARAMETER
  now realizes its element as the faithful WhyML type — `array string` (resp. `array real`) — so a
  use-site read `a[i]` reads the faithful element (`a[i] : string` / `: real`), matching a str/float
  return. This is the ONE-LEVEL-UP flat analog of the nested-list `array (seq τ)` work: Module5's new
  `_m5_get_list_flat_elem_whyml` maps a `List[str]`→`"string"` / `List[float]`→`"real"` param
  annotation into a new IR field `param_list_flat_elem`; Module6's `_param_type_str` consumes it
  (right after the nested `_list_nested_elem` branch) to emit `array {τ}`. The subscript READ path is
  UNCHANGED (the `is_array` branch's `Array.get` is element-polymorphic). A flat `List[int]`/
  `List[bool]` has NO entry (→ byte-identical `array int`), and a nested `List[<container>]` is owned
  by `_m5_get_list_nested_elem_whyml` (→ `array (seq τ)`, unchanged).
- **Construct / position:** element read `a[i]` on a `List[str]`/`List[float]` param at a
  faithfully-typed use site (str/real return).
- **Was:** `let f (a: array int) … : string = a[i]` — `a[i] : int` vs return `: string`
  (resp. `: real`) → internally inconsistent, ill-typed WhyML (TYPEERR).
- **Now:** `let f (a: array string) … : string = a[i]` (resp. `array real` / `: real`) — the element
  read type-checks AND the faithful element property `\result == a[i]` is provable.
- **Faithful target realized:** `τ(List[str]) = array string`, `τ(List[float]) = array real` (the
  flat leaf case the nested campaign skipped). Derivation is a native `array` read; SMT discharges it
  directly — **no cited lemma needed**.
- **Class / severity:** COLLAPSED-with-consumer / 3 (was).
- **Verdict flips (now):**
  - `getting-better/wrong-lowering/wl04_list_str_elem_COLLAPSED.py` → **PROVEN** (bounds requires +
    faithful `\result == a[i]` at `string`). Was TYPEERR.
  - `getting-better/wrong-lowering/wl04_list_float_elem_COLLAPSED.py` → **PROVEN** at `real`. Was
    TYPEERR.
  - Baseline `List[int]` param element read → **STAYS** `array int` / PROVEN (byte-identical).
- **SMT-feasibility spike:** `test-suite/corpus/conformance/spikes/wl04_list_flat_elem_spike.mlw` —
  the `array string` / `array real` element read (`a[i] == "x"` / `a[i] == 1.5`, read-after-write,
  slot independence) all Valid on **both** Alt-Ergo AND Z3 (no cited lemma).
- **Regression locks (reference corpus):** `test-suite/corpus/pycsl-reference/0817.py` (POSITIVE —
  `List[str]` element reads, `\result == a[i]`), `0818.py` (POSITIVE — `List[float]` element reads,
  fractional value preserved), and `0819.py` (NEGATIVE, `# pycsl-expected: FAIL` — a false
  element-content conflation `a[0]` claimed `== a[1]`, must stay UNPROVEN).
- **Emission differential:** the full 697-file `pycsl-reference` corpus emits BYTE-IDENTICALLY
  (verified via `bin/byte-diff-sweep.sh`); no corpus program has a flat `List[str]`/`List[float]`
  PARAM (0746 is a `Dict[str, List[str]]` FIELD; 0804 is a nested `List[List[str]]` param → the
  nested path) → additive.
- **LOCALS / RETURN via a LIST LITERAL (WL-04a) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`). A
  `List[str]`/`List[float]` LOCAL and a `-> List[str]`/`-> List[float]` RETURN built by a LIST
  LITERAL (`a = ["x", "y"]`, `return ["a", "b"]`) previously collapsed the string ELEMENTS to hashed
  ints (`Array.make 2 (747471683)`) and truncated float elements (`[1.5,2.5]`, `a[1]` folded to `2`),
  a DISTINCT construction surface from the WL-04 PARAMETER element. The list-literal lowering
  (`module6_whyml/expressions.py::_expr_to_whyml`, `ArrayLitExpr` arm) now detects an ALL-string
  (resp. ALL-float) literal and builds `array string` (resp. `array real`) with the FAITHFUL element
  values — NOT `_coerce_to_int` hashing/truncation. The indexed-read constant-fold
  (`module6_whyml/types.py::_track_collection_metadata`) folds a pure-float literal to the faithful
  real (`a[1]` → `2.5`, not `2`). A `-> List[float]` return annotation now resolves to `array real`
  (Module5 `_m5_get_list_flat_elem_whyml` fallback for the return element →
  `functions.py::_compute_return_type` `array real` arm; the `-> List[str]` → `array string` arm
  already existed), and a contract `\result[i]` on ANY `array τ` return lowers to a native
  `Array.get` (widened from `array int`-only, `expressions.py::_handle_subscript` L0). Drivers
  `getting-better/wrong-lowering/wl04a_list_literal_{str_local,str_return,float_local}_*.py` →
  PROVEN; false-content twin → UNPROVEN. `List[int]` literals stay `array int` BYTE-IDENTICAL
  (full 704-file corpus emits byte-identically; only the 3 new locks are new). Reference locks:
  `0826.py` (POSITIVE `List[str]` literal local + `-> List[str]` return element read), `0827.py`
  (POSITIVE `List[float]` literal local + `-> List[float]` return), `0828.py` (NEGATIVE
  `# pycsl-expected: FAIL` false element-content twin). SMT spike
  `test-suite/corpus/conformance/spikes/wl04a_list_literal_elem_spike.mlw` (Valid on Alt-Ergo AND
  Z3, no cited lemma). STILL OUT OF SCOPE: a `List[<record>]` literal (now covered by **WL-04c**);
  a MIXED-element literal (`[1, "x"]` / `[1, 2.5]` / `[1, Point(2,3)]`) is now a **DOCUMENTED SOUND
  BOUNDARY — WL-04g** (below): it is REJECTED fail-closed (was int-coercion, which was UNSOUND for
  the str case).
- **MIXED-element literal (WL-04g) — ✅ DOCUMENTED SOUND BOUNDARY / soundness FIX** (branch
  `ghost-assign-bc6`). A HETEROGENEOUS list literal (`[1, "x"]`, `[1, 2.5]`, `[1, Point(2, 3)]`) has
  NO faithful `array τ` element type — a Python list is heterogeneous, a WhyML `array` is
  HOMOGENEOUS. The audit found the previous int-coercion default was **SEVERITY-1 UNSOUND for the
  int+str case**: `[1, "x"]` hash-coerced `"x"` to a WELL-TYPED int (`976090257` under
  `PYTHONHASHSEED=0`) and built `array int`, so a contract `\result == 976090257` on `a[1]` PROVED —
  a claim FALSE of real Python (`a[1]` is the string `"x"`). Witness:
  `getting-better/wrong-lowering/wl04g_mixed_int_str_UNSOUND.py` was **PROVEN** before the fix. (The
  int+float and int+record cases already failed closed via a Why3 TYPEERR — the float/record cannot
  type into `array int` — but were ugly broken emissions.) **FIX (fail-closed, additive):** a new
  guard `module6_whyml/expressions.py::_mixed_literal_reject_kind`, called from the `ArrayLitExpr`
  int-coercion FALLBACK, detects any element whose faithful type is non-int (a `str` literal, a
  `float` `Number`, a `Tuple`, or a known-record constructor `Call`) — which, since every UNIFORM
  non-int shape (all-str/all-float WL-04a, all-record WL-04c, all-equal-arity-tuple) is already
  claimed above, PROVES the literal is mixed — and raises a clear `PyCSLSemanticError` naming the
  offending element kind and directing the user to a homogeneous list, a `Tuple` (fixed-arity
  heterogeneous slots), or a record/`@dataclass` (heterogeneous fields). A homogeneous
  all-int/bool/expression literal is NOT flagged (byte-identical `array int`). Verdict flips: the
  three false-twin drivers `wl04g_mixed_int_{str,float,record}_falsetwin.py` and the unsound witness
  `wl04g_mixed_int_str_UNSOUND.py` are all **REJECTED** (no false content claim proves); the positive
  regression `wl04g_homogeneous_int_POSITIVE.py` stays **PROVEN** (no over-rejection). Boundary spike
  `test-suite/corpus/conformance/spikes/wl04g_mixed_literal_boundary_spike.mlw` (the sound
  homogeneous `array int` Valid on **both** Alt-Ergo AND Z3; the mixed-float array is Why3
  TYPE-rejected — the boundary witness). Reference locks: `0850.py` (POSITIVE homogeneous — guards
  over-rejection), `0851.py` (NEGATIVE `# pycsl-expected: FAIL` — int+str, the headline soundness
  lock), `0852.py` (NEGATIVE int+float), `0853.py` (NEGATIVE int+record). Full-corpus byte-diff = 0
  (no corpus program is a mixed literal). A future faithful model would require a heterogeneous-sum
  element type (a Why3 variant over the element categories), well beyond the homogeneous `array`
  model. Docs: τ-table + §T.6.1 concrete-array row in `pycsl-translational-reference.md`, the
  `§ MIXED-element list literal` rule in `pycsl-static-semantics-reference.md`.
- **Record element (WL-04b) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`). A flat `List[<record>]`
  PARAMETER (and pass-through RETURN) — where the element `R` is a KNOWN record: a user
  `@dataclass`/`NamedTuple` class OR a recognized `Tuple[T1, …, Tn]` (WL-03's synthesized per-slot
  record `pytuple_<tags>`) — is now realized as **`array <record-whyml>`** (was the collapsed
  `array int` with an opaque `get_field`/`subscript_get` element read), so `a[i]` reads a REAL
  record and `a[i].field` / `a[i][k]` projects the FAITHFUL field. This is the record-leaf analog of
  the str/float flat model above and of the WL-03 tuple per-slot record. Threading: Module5
  `_m5_get_list_record_elem` maps a `List[R]` element to the record CLASS NAME into
  `param_list_flat_elem` (using the pre-collected `_m5_record_class_names` + the WL-03
  `_m5_tuple_slot_tags`); a record-list param is subtracted from the 2-D `matrix int` detection
  (so `a[i][1]` on a `List[Tuple[…]]` is a slot read, not a matrix cell); Module6 `_param_type_str`
  resolves the record name via `_record_types` → `array <whyml>` and registers `_record_array_params`;
  `_handle_attribute_expr` lowers `a[i].field` to the native `(let _rec_ = a[i] in _rec_.<label>)`
  and `_namedtuple_positional_access` lowers `a[i][k]` to the k-th slot; `_compute_return_type`
  resolves a `-> List[R]` return to `array <whyml>`. **Why3 constraint (SMT-established):** Why3
  FORBIDS a MUTABLE element inside `array`, so a record used as a `List[<record>]` element is emitted
  **PURE** (immutable fields) — Module5 records the names in `list_element_record_types`; the preamble
  drops `mutable` for exactly those records (byte-identical for every record NOT used as a list
  element; tuples/NamedTuples are immutable, and a `List[<dataclass>]` reads its fields only, so a
  field-mutated dataclass-in-a-list fails CLOSED at Why3 type-check — never a silent unsound update).
  Verdict flips: `getting-better/wrong-lowering/wl04b_list_record_elem_COLLAPSED.py` UNPROVEN →
  **PROVEN**; `wl04b_list_tuple_elem_COLLAPSED.py` TYPEERR → **PROVEN**; false-twin
  `wl04b_list_record_falsetwin.py` → **UNPROVEN**. SMT spike
  `test-suite/corpus/conformance/spikes/wl04b_list_record_elem_spike.mlw` (an `array <record>` element
  field read + read-after-write independence, Valid on **both** Alt-Ergo AND Z3, no cited lemma).
  Reference locks: `0829.py` (POSITIVE `List[<dataclass>]` `a[i].field`), `0830.py` (POSITIVE
  `List[Tuple[int,str]]` `a[i][k]` slot), `0831.py` (NEGATIVE `# pycsl-expected: FAIL` false
  cross-field conflation). **Emission-differential:** the ONLY corpus programs whose emission changes
  are the three pre-existing `List[Point]` projection programs `0769`/`0770`/`0771` (they NOW prove the
  content law via the native `(a[i]).x` projection instead of the opaque `get_x`, and the false twin
  0771 STAYS UNPROVEN); every OTHER of the 707 corpus files emits BYTE-IDENTICALLY. **STILL OUT OF
  SCOPE (documented residuals):** the `List[<record>]` LITERAL is now covered by **WL-04c** (below); a
  FILTERED projection comprehension over a record source (`[p.x for p in a if …]`) is now covered by
  **WL-04d** (below); a `List[<plain-class-with-__init__>]` element is now covered by **WL-04e**
  (below); a record element with a `float` field slot is now covered by **WL-03b** (below — the WL-03
  slot recognition was int/bool/str only, now int/bool/str/float); a record element with a CONTAINER
  field slot is a documented boundary (**WL-03b** below). str/float (WL-04) and record (WL-04b) are the
  covered flat leaves.
- **Record LITERAL (WL-04c) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`). A `List[<record>]` LITERAL
  whose elements are ALL full-arity positional constructor CALLS to the SAME CONTENT-FAITHFUL record —
  `a = [Point(1, 2), Point(3, 4)]` (LOCAL) or `return [Point(1, 2), Point(3, 4)]` (with `-> List[Point]`)
  — previously ran every element through `_coerce_to_int`, so the record-constructor element collapsed
  to an opaque int and `a[i].field` (local) / `\result[i].field` (return) was content-opaque / ill-typed
  at a record use site (TYPEERR). This is the CONSTRUCTION analog of WL-04b (the flat `List[<record>]`
  PARAMETER element) and the record-leaf twin of WL-04a (str/float list-literal). The list-literal seam
  now threads the record CONSTRUCTOR: `module6_whyml/expressions.py::_expr_to_whyml` (`ArrayLitExpr`
  arm), gated by the new `_record_ctor_list_elem`, builds `array <record>` with each element the
  FAITHFUL record literal (`{ x = 1; y = 2 }`, args threaded via `_call_record_constructor`);
  `types.py::_track_collection_metadata` registers the local in the new `_record_array_locals`, so
  `a[i].field` / `a[i][k]` project natively (via the extended `_handle_attribute_expr` +
  `_namedtuple_positional_access`, the local twin of `_record_array_params`); `\result[i].field` on a
  `-> List[R]` return (whose `array <record>` type WL-04b already resolves via `_compute_return_type`)
  projects via the widened `_handle_attribute_expr` Result-subscript arm. The element record is emitted
  **PURE** (Why3 forbids a mutable element inside `array`): Module5 `_m5_list_literal_record_elem`,
  computed AFTER `generic_visit` (so class-based NamedTuples are populated), adds it to
  `list_element_record_types`. **FAITHFUL CONSTRUCTION IS REQUIRED:** only a record whose constructor
  sets EVERY field from a positional param (a `NamedTuple`, a recognized `Tuple`, an explicit-`__init__`
  positional class) is threaded; a `@dataclass` with no explicit `__init__` DROPS its ctor args (a
  SEPARATE pre-existing gap — even standalone `Point(1, 2).x` currently proves `== 0` unsoundly), so its
  literal element is NOT content-faithful and stays **FAIL-CLOSED** (opaque / TYPEERR — never threaded
  into native projection, so the array path is never a silent unsound `a[0].x == 0`). Verdict flips:
  `getting-better/wrong-lowering/wl04c_list_record_literal_COLLAPSED.py` TYPEERR → **PROVEN**; false-twin
  `wl04c_list_record_literal_falsetwin.py` → **UNPROVEN**. SMT spike
  `test-suite/corpus/conformance/spikes/wl04c_list_record_literal_spike.mlw` (a record-list-LITERAL
  element/return field read + read-after-write independence + cross-element distinctness, Valid on
  **both** Alt-Ergo AND Z3, no cited lemma). Reference locks: `0839.py` (POSITIVE — local literal
  `a[i].field` + `-> List[Point]` return `\result[i].field`), `0840.py` (NEGATIVE `# pycsl-expected:
  FAIL` — a false cross-field conflation). **Emission-differential:** the ONLY corpus files whose
  emission changes are the two NEW locks `0839`/`0840`; every OTHER of the 718 pre-existing corpus files
  emits BYTE-IDENTICALLY (`bin/byte-diff-sweep.sh`, before/after). No new axiom; `\trusted`
  non-increasing; doc-coherency green. **STILL OUT OF SCOPE (documented residuals):** a `@dataclass`-ctor
  literal (blocked on the dataclass positional-ctor-capture gap — a distinct pre-existing unsoundness
  worth its own fix), and a MIXED-record / keyword-arg literal keep the fail-closed (int-collapse /
  opaque / TYPEERR) model.
- **FILTERED record-projection comprehension (WL-04d) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`). A
  FILTERED projection comprehension `[p.x for p in a if <cond(p)>]` over a flat `List[<record>]` source
  `a` (`array <record>`, WL-04b) previously fell through `_content_comp`'s record branch to the opaque
  `val list_comp (x:int):int` (an opaque INT), so a `-> List[int]` return (`array int`) was returned an
  int → ill-typed WhyML (TYPEERR — fail-closed but UNUSABLE: neither the length bound nor any content
  fact was expressible). The RESULT LENGTH of a filter is DATA-DEPENDENT (`0 <= len(result) <= len(a)`),
  so an exact length / per-index content law is genuinely NOT provable and is NOT claimed (claiming
  either would be UNSOUND). What IS soundly dischargeable — and now emitted
  (`module6_whyml/expressions.py::_filter_record_proj_law`, a per-instance `list_content_comp_<n>` val)
  — is the length BOUND `Array.length result <= Array.length src` PLUS a membership+predicate+projection
  EXISTENTIAL: `forall i. 0<=i<len result -> exists j. 0<=j<len src /\ (let p = src[j] in <cond(p)> /\
  result[i] = <p.field>)`. Every output came from some retained input (Python semantics), an honest
  under-approximation (the source index is lost to compaction, so NO order/index claim is made). From
  it the FILTER CONSEQUENCE transfers to the projected result whenever the predicate constrains the
  projected field (`[p.x for p in a if p.x > 0]` PROVES every result element `> 0`). The element and
  predicate are lowered NATIVELY over the record binder (`(src[j]).field`, via `_push_quant_binder`;
  `_comp_cond_pure_bool` extended with the `getters`/`user_funcs` accumulators so a record-field
  predicate `p.x > 0` lifts). A predicate that does NOT lift to a pure-bool term over the target keeps
  the SOUND length-bound-only law (still `array int` — never the prior TYPEERR). Verdict flips:
  `getting-better/wrong-lowering/wl04d_filtered_record_proj_COLLAPSED.py` TYPEERR → **PROVEN** (length
  bound + `\result[i] > 0` filter-consequence + the membership existential); false-twin
  `wl04d_filtered_record_proj_falsetwin.py` (claims `len(\result) == len(a)`) → **UNPROVEN**. SMT spike
  `test-suite/corpus/conformance/spikes/wl04d_filtered_record_proj_spike.mlw` (length bound +
  filter-consequence transfer + membership, Valid on **both** Alt-Ergo AND Z3, no cited lemma; the
  length-EQUALITY and per-index-content false twins stay Unknown/Timeout — NOT entailed). Reference
  locks: `0841.py` (POSITIVE — length bound + all-positive filter consequence + existential membership,
  plus a two-projection predicate), `0842.py` (NEGATIVE `# pycsl-expected: FAIL` — a false per-index
  content claim `\result[i] == a[i].x`). **Emission-differential:** the ONLY corpus files whose emission
  changes are the two NEW locks `0841`/`0842`; every OTHER of the 720 pre-existing corpus files emits
  BYTE-IDENTICALLY (`bin/byte-diff-sweep.sh`, before/after diff = 0). No new axiom; `\trusted`
  non-increasing; doc-coherency green. **STILL OUT OF SCOPE (documented residuals):** a FILTERED
  TUPLE-SLOT projection (`[t[0] for t in a if …]`, the element is a subscript not an attribute — the
  unfiltered tuple-slot projection is itself already out of the `.field` projection scope), and a
  projection whose element is not a pure-int field term keep the opaque / length-bound-only model.
- **PLAIN-CLASS element (WL-04e) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`). A flat `List[Point]`
  PARAMETER (and pass-through RETURN) where `Point` is a PLAIN class with an explicit positional
  `__init__` (`class Point: def __init__(self, x, y): self.x = x; self.y = y`) — NOT a
  `@dataclass`/`NamedTuple`/recognized `Tuple` — was NOT recognized as a list-element record, so it
  collapsed to `array int` and `a[i].x` read the opaque `get_x(a[i])`. Such a class is ALREADY emitted
  as a record `type_decl` by `visit_ClassDef` and its constructor is CONTENT-FAITHFUL (verified before
  relying on it: `Point(1, 2).x` proves `== 1` and NOT `== 0` — unlike a `@dataclass` whose ctor drops
  its args), so it now resolves to **`array <record>`** exactly like WL-04b: `a[i]` reads a REAL
  `point`, `a[i].field` projects the faithful field, and a constructed record STORED into an array
  element (`a[0] = Point(5, 6)` → the faithful `{ x = 5; y = 6 }`, reusing WL-04c's ctor threading)
  reads its written field back. **Single recognition seam:** `_m5_is_plain_positional_record_class`
  (a pre-`generic_visit` scan of `node.body`, mirroring the dataclass/NamedTuple pre-scan) adds the
  class name to `_m5_record_class_names`, so the UNCHANGED WL-04b `_m5_get_list_record_elem` →
  `_param_type_str` → `array <record>` → `_record_array_params` → `_handle_attribute_expr` threading
  applies — NO new Module6 code. **FAITHFUL-ONLY recognition:** a plain `__init__` whose ANY
  `self.<attr>` is set from a non-positional-param expression (constant / computation / keyword-only
  param) is REJECTED and kept at the `array int` collapse (fail-closed). The element record is emitted
  **PURE** (`list_element_record_types`); a field-mutated plain-class-in-a-list has the SAME
  fail-closed posture as WL-04b — BYTE-IDENTICAL to the `@dataclass` path (the element write is
  dropped, the post-mutation claim UNPROVEN — never a silent unsound update). Verdict flips:
  `getting-better/wrong-lowering/wl04e_list_plainclass_elem_COLLAPSED.py` (read law + store-read-back)
  → **PROVEN**; false-twin `wl04e_list_plainclass_elem_falsetwin.py` (`\result == a[1].x`
  cross-element conflation) → **UNPROVEN**. SMT spike
  `test-suite/corpus/conformance/spikes/wl04e_list_plainclass_elem_spike.mlw` (an `array <record>`
  element read + plain-ctor store-read-back + read-after-write independence + cross-element
  distinctness, Valid on **both** Alt-Ergo AND Z3, no cited lemma). Reference locks: `0843.py`
  (POSITIVE — `List[Point]` param read law + store-read-back), `0844.py` (NEGATIVE `# pycsl-expected:
  FAIL` — false cross-element conflation). **Emission-differential:** the ONLY corpus files whose
  emission changes are the two NEW locks `0843`/`0844`; every OTHER of the 722 pre-existing corpus
  files emits BYTE-IDENTICALLY (`bin/byte-diff-sweep.sh`, before/after diff = 0 — a plain class NOT
  used as a flat `List[R]` element never reaches `_m5_get_list_record_elem`, so the additivity is
  structural). No new axiom; `\trusted` non-increasing; doc-coherency green. **STILL OUT OF SCOPE
  (documented residuals):** a plain-`__init__` class whose ctor is NOT purely positional (a field from
  a constant / computation / keyword-only param) keeps the prior model; a record slot of `float` type
  is now the faithful `real` (WL-03b below); a record slot of CONTAINER type is a documented boundary
  (WL-03b below).
- **NESTED-list NON-int-leaf inner mutation (WL-04f) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`).
  The nested-list feature had int-leaf `List[List[int]]` inner mutation `a[i][j]=v` via the mutable
  built-in `matrix int` (commit `9f03aae7`, drivers 0802/0803); the NON-int-leaf twin (`List[List[str]]`
  ~ `array (seq string)`, `List[List[float]]` ~ `array (seq real)`) was a REJECTED boundary (the inner
  `seq` is a PURE/immutable Why3 value; `array (array τ)` is Why3 TYPE-rejected). WL-04f LANDS it via
  **option (c): an outer-array store of a functionally-updated inner seq** — `a[i][j]=v`→
  `a[i] <- Seq.set a[i] j v`. The OUTER `array` IS mutable, so the write is a native `Array.set`
  effect (`writes {a}`, caller-visible — matching Python's in-place semantics); the inner `seq` stays
  PURE. Reads are UNCHANGED (`a[i][j]`→`Seq.get a[i] j`); `Seq.set`'s `requires 0 <= j < length` is the
  IndexError obligation. **Single Module6 seam:** `_handle_array_set_stmt` (module6_whyml/statements.py)
  gains a leading branch guarded on a `seq `-leaf `_list_nested_elem` param + non-String indices — NO
  Module5 change (the param already STAYS on `param_list_nested_elem` when non-int-leaf inner-mutated,
  since only `seq int` is matrix-routed). **SOUNDNESS — no false claim under aliasing (rigorously
  established):** the value-semantics store diverges from Python's reference mutation ONLY under inner
  aliasing, which is UNEXPRESSIBLE in PyCSL — an inner list can be neither bound to a local (`b = a[i]`
  type-fails: a local defaults to `int`) nor shared across outer slots (`a = [row, row]` type-fails:
  `array (array τ)` is rejected). Both routes were probed and FAIL CLOSED, so every expressible
  post-state is faithful. Gate-B spike `test-suite/corpus/conformance/spikes/nested-list-inner-mutable-seq.mlw`
  (write-read-back + outer-frame + inner-frame + dims-preservation Valid on **both** Alt-Ergo AND Z3;
  false twin Timeout/Unknown = correctly unproven; no new axiom — Seq/Array laws are Why3 stdlib).
  Reference locks: `0804.py` REPURPOSED from NEGATIVE-rejection to POSITIVE `List[List[str]]` read-back;
  `0847.py` (POSITIVE `List[List[float]]` read-back + non-aliasing frame); `0848.py` (NEGATIVE
  `# pycsl-expected: FAIL` — false twin, post cell `!= v` stays UNPROVEN); `0849.py` (NEGATIVE — map-leaf
  `List[Dict[int,int]]` inner item write `a[i][k]=v` stays fail-closed TYPEERR). **Emission-differential:**
  the ONLY pre-existing corpus file whose emission changes is `0804.mlw` (before/after
  `bin/byte-diff-sweep.sh` diff = exactly `0804`); every other of the 726 corpus files is BYTE-IDENTICAL
  (a nested param that is not `seq `-leaf inner-mutated never reaches the new branch). No new axiom;
  `\trusted` non-increasing. **STILL OUT OF SCOPE (documented residuals):** a **MAP leaf**
  (`List[Dict[…]]`) inner item write is fail-closed (0849) — the map analog `a[i] <- map_update a[i] k
  (Some v)` is an unspiked follow-on; the `seq int` leaf routes to `matrix int` (WL nested-list-mutable,
  unchanged); `a[i].append(..)` (shape-change) and ragged in-place mutation stay OPAQUE/out-of-model
  (no false post-state claim); deeper-than-2 (`a[i][j][k]=v`) inner mutation is beyond scope (read is
  depth-bounded; write not implemented → fail-closed).
- **FLOAT record/tuple FIELD SLOT (WL-03b) — ✅ IMPLEMENTED** (branch `ghost-assign-bc6`). The WL-03
  synthesized per-slot record and the WL-04b `List[<record>]` element/record models recognized
  slot/field types **int/bool/str ONLY**, so a `float` field slot collapsed to `int` — an UNSOUND leak
  that TRUNCATED a fractional read: `t[1]` of a `Tuple[int, float]`, and `q.f` / `a[i].f` of a
  `@dataclass`/`self.f: float` record, holding `2.5`, read `2` where real Python reads `2.5`. WL-03b
  realizes a `float` field slot as the faithful Why3 **`real`** (τ(float)=real, no-more-int Stage D).
  **Threading (3 small seams, NO new Module6 handler):** Module5 `_M5_TUPLE_SLOT_TAGS` maps
  `float`→`real` (so a recognized `Tuple[int, float]` synthesizes `pytuple_int_real = { field0: int;
  field1: real }`) and `_field_type_from_annotation` maps a `float`-annotated field to the `real` tag;
  the preamble record emitter (`_emit_type_decls`) maps that tag to a `real` field; `_build_witness_str`
  gets a `0.0` real witness (only reached by a float-field record that ALSO carries a class invariant).
  The projection `t[1]` (via `_namedtuple_positional_access`) / `q.f` / `a[i].f` (WL-04b
  `_handle_attribute_expr`, unchanged) then reads a `real`; the float comparison routes through Why3
  `real` equality (a `2.5` literal on either side drives the real `=`, exactly as the WL-04 `array
  real` element read). **Because `real` is a PURE type, a record with a `real` field is legal at an
  `array` element position** — the WL-04b PURE-element constraint is preserved (a `real`-field record
  used as a `List[R]` element is emitted PURE). A float field read used where an int is expected stays
  a fail-closed real-vs-int TYPEERR (never a silent truncation). Verdict flips:
  `getting-better/wrong-lowering/wl03b_float_record_slot_COLLAPSED.py` (`Tuple[int,float]` slot +
  plain record float field + `List[R]` float-field element, `\result == 2.5`) → **PROVEN**; false-twin
  `wl03b_float_record_slot_falsetwin.py` (the int-truncation `\result == 2.0` claim) → **UNPROVEN**.
  SMT spike `test-suite/corpus/conformance/spikes/wl03b_float_record_slot_spike.mlw` (a real tuple
  slot, a plain real-field record, and a PURE real-field record at an `array` element position —
  read + read-after-write independence + no-truncation + cross-slot distinctness, 7 goals Valid on
  **both** Alt-Ergo AND Z3, no cited lemma). Reference locks: `0845.py` (POSITIVE), `0846.py`
  (NEGATIVE `# pycsl-expected: FAIL` — the int-truncation twin). **Emission-differential:** the ONLY
  corpus files added are the two NEW locks `0845`/`0846`; every pre-existing corpus file (724 sweep)
  emits **BYTE-IDENTICALLY** (`bin/byte-diff-sweep.sh`, before/after diff = 0 — the corpus has NO
  `float` record/tuple field, so the additivity is structural). No new axiom; `\trusted`
  non-increasing; doc-coherency green.
- **CONTAINER record FIELD SLOT (WL-03b) — 📎 DOCUMENTED BOUNDARY.** A record slot of CONTAINER type
  (`Point` with a `List[int]` field, used as a `List[Point]` element so the record sits at an `array`
  element position) is NOT lowered faithfully; it is a rigorously-argued boundary. **Exact Why3 fact
  (FACT 1, the rejection):** the faithful mutable-Python-list field model is `array int` (what the
  corpus's standalone container fields already use, and what supports `p.f[i] = v` / `p.f.append(..)`);
  a record `{ pn: int; mutable pf: array int }` placed at an `array` element position is TYPE-REJECTED
  by Why3 — *"This application instantiates pure type variable 'a with a mutable type point_mut"* — the
  SAME `array (array τ)` / mutable-element rejection the nested-list project met (`array` instantiates a
  PURE type variable; a record with ANY mutable component is a mutable type). **Exact Why3 fact (FACT
  2, feasible-but-out-of-scope):** a PURE `seq int` field DOES type-check and its read PROVES on both
  Alt-Ergo AND Z3 (spike `test-suite/corpus/conformance/spikes/wl03b_container_slot_boundary.mlw`), so
  a READ-ONLY container-field representation is SMT-sound. **Why it stays a boundary:** adopting the
  pure-`seq`/`map` field requires a usage-dependent MUTABLE-vs-PURE per-record representation split
  (the record-field analog of the nested-list `array (seq τ)` vs `matrix int` split) — the field must
  fall back to pure `seq` ONLY where the record is an `array` element AND the field is never mutated, a
  field mutation must be REJECTED (fail-closed, else unsound), and it must not regress the existing
  mutable `array int` standalone container-field records (additivity). That split is a distinct, larger
  project. A future faithful model would thread that per-record usage analysis; for now the container
  slot keeps the prior (int-collapse / opaque `array int`) model, fail-closed.
- **Dedup:** none (we-are-getting-better.md #6/#7 are IR-node list attrs in the mirror, a different
  surface).

### WL-05 — dict / set PARAMETER item-mutation — ✅ FIXED → ✅✅ WL-05b: now FAITHFULLY SUPPORTED (caller-visible)
- **Status:** ✅✅ **FAITHFULLY SUPPORTED** (WL-05b, branch `ghost-assign-bc6`). The earlier WL-05 fix
  was a CLEAN REJECTION (sound but conservative). WL-05b IMPLEMENTS the faithful model the rejection
  deferred: Python passes dicts/sets BY REFERENCE, so an inner-mutated dict/set PARAMETER is now
  modelled as a caller-visible **MUTABLE `ref (map κ (option ν))`** with a sound **`writes {d}`**
  frame — the mutation escapes to the caller. USAGE-DRIVEN: only a param the body INNER-mutates is
  promoted; a READ-ONLY dict/set param keeps the by-value `map …` type (BYTE-IDENTICAL).
- **Why3 representation (SMT-feasibility spike, PROVEN on Alt-Ergo + Z3):** a param
  `d: ref (map κ (option ν))` with `writes {d}`; `d[k]=v` → `d := map_update_some !d k v`; reads →
  `!d` / `Map.get !d k` UNIFORMLY (the WL-05 bug was the inconsistent `d :=`/bare-`d` mix — fixed by
  the uniform ref discipline). Set param `.add`/`.discard`/`.remove` likewise on `ref (map int
  (option int))`. Both `(mutate; read-back) = Some v` AND caller-visibility (a caller passing a ref
  observes the post-state) prove on BOTH provers. Spike fixture:
  `test-suite/corpus/conformance/spikes/wl05b_param_mut_spike.mlw`.
- **Construct / position:** `d[k] = v` (`ArraySet`) — and the set twin `s.add(x)`/`s.discard(x)`/
  `s.remove(x)` — on a `Dict[...]`/`Set[...]` *parameter* of a STANDALONE function.
- **Was (WL-05):** `d := map_update_some !d k v; … Map.get d k` — treated the by-value param as a
  mutable `ref` (`d :=`, `!d`) AND then read bare `d` → ill-typed. WL-05 rejected it cleanly.
- **Now (WL-05b):** the emitter (1) DETECTS inner-mutated dict/set params via a module-level FIXPOINT
  (direct item-mutation + transitive param forwarding: if A forwards its param to a callee's mutated
  position, A's param is mutated too — the by-reference escape is transitive); (2) emits the promoted
  params as `ref (map …)` in the signature (`functions.py::_param_type_str`) with a `writes {…}` frame
  (`_emit_function`); (3) routes them through the local-collection discipline (`_dict_locals`) so all
  reads/writes deref uniformly (`!d`); (4) at each call site passes the BARE ref (not `!d`) for a
  callee's mutated position (`expressions.py::_handle_call_expr`) so the mutation escapes. Methods are
  OUT OF SCOPE (their param types also feed the abstract-op call-contract map, which the ref promotion
  would desync) → a mutated dict/set METHOD param keeps the WL-05 rejection / @mutable_state no-op.
- **Class / severity:** WRONG-REPR / 4 (was) → now FAITHFULLY SUPPORTED (caller-visible, sound frame,
  non-vacuous: a false post-mutation claim FAILS).
- **Verdict flips (now):**
  - `wl05_dict_param_mut_WRONGREPR.py` → **PROVEN** (was REJECTED; faithful `d[k]=v` write-read-back).
  - `wl05_set_param_mut_WRONGREPR.py` (set twin) → **PROVEN** (was REJECTED).
  - Baseline `wl05_dict_local_FAITHFUL.py` (LOCAL dict write-read-back) → **STAYS PROVEN**.
- **Regression locks (reference corpus):** `0820.py` (POSITIVE — dict param `d[k]=v` write-read-back
  proves; was NEGATIVE `# pycsl-expected: FAIL` under WL-05), `0821.py` (POSITIVE — set param `s.add`
  + membership consequence proves; was NEGATIVE), `0822.py`/`0823.py` (POSITIVE — LOCAL dict/set still
  prove, unchanged), `0832.py` (POSITIVE — dict param mutation ESCAPES to the caller: two functions,
  caller observes the write via the callee's `ensures d["a"]==5`), `0833.py` (POSITIVE — set twin
  caller-visibility), `0834.py` (NEGATIVE, `# pycsl-expected: FAIL` — a FALSE post-mutation claim
  `ensures d["a"]==6` for a body writing `5` must FAIL: the frame is genuinely checked, non-vacuous).
- **Emission differential:** the full `pycsl-reference` corpus emits BYTE-IDENTICALLY EXCEPT the two
  drivers that item-mutate a dict/set param (0820, 0821 — which previously REJECTED and emitted no
  `.mlw`, now emit and prove). Every read-only-collection and non-param-mutation program is unchanged
  (verified via `bin/byte-diff-sweep.sh`: 0 content diffs on all common files). NO new axiom;
  `map_update_some`/`map_update_none` are the existing local-collection ops. `\trusted` non-increasing.
- **Dedup:** none. WL-05's rejection path (`_reject_param_collection_mutation`) is RETAINED for the
  still-out-of-scope cases (mutated dict/set METHOD params, and the record/list param-mutation class).

### WL-06 — `bytes` subscript `b[i]` emits `subscript_get(int,int)` on an `array int` value — ✅ FIXED (WL-06 coherence) + ✅ WL-06b (faithful byte CONTENT of a literal + immutability)
- **Status:** ✅ **FIXED** (branch `ghost-assign-bc6`). A `bytes`/`bytearray` value is the τ-blessed
  `bytes=int†` array-int-backed buffer (`b : array int` — KEPT, the coarsening is unchanged); the
  defect was that a subscript READ `b[i]` routed to the opaque `subscript_get (x:int)(i:int):int`
  applied to `b : array int` (an `array int` vs `int` type error). The read now lowers to a native
  `Array.get b i` (a coherent `int` byte read) — the SAME array-read path already used for `list`/array
  params. `len(b)` likewise lowers to `Array.length b` (was the unbound `iter_length` stub), so a bounds
  `requires i < len(b)` type-checks. In `module6_whyml/expressions.py`, `_handle_subscript` and the `len`
  handler now recognize a `bytes`/`bytearray` symbol-table type on the same array branch as `list`.
- **Construct / position:** `b[i]` read (and `len(b)`) on a `bytes`/`bytearray` parameter.
- **Was:** `let f (b: array int) … : int = (subscript_get b i)` — `subscript_get` expects `x:int` but
  is applied to `b : array int` → ill-typed WhyML (TYPEERR): the read was BOTH un-verifiable AND
  internally inconsistent.
- **Now:** `let f (b: array int) … : int = b[i]` (`Array.get`, guarded by an IndexError bounds VC) —
  the read type-checks AND, under a bounds `requires`, the deterministic read property `\result == b[i]`
  is PROVABLE.
- **Faithful target realized (COHERENCE — WL-06; byte CONTENT of a LITERAL — WL-06b):** `τ(bytes)=int†`
  (the coarse `array int` SHAPE) is unchanged. WL-06 delivered COHERENCE (the read type-checks as a
  sound `int`). **WL-06b (this follow-on) delivers faithful byte CONTENT for a `bytes` LITERAL:** a
  `bytes` literal lowers to an `array int` built from the REAL byte values (Module5 `_py_expr_constant`
  → `ArrayLit`; Module6 → `Array.make n v0; a[1] <- v1; …`), so a content read PROVES the ACTUAL byte
  (`b"abc"[0] == 97`, `b"abc"[1] == 98`, `b"\x01\xff\x80"[1] == 255`), the byte-RANGE invariant
  `0 <= b[i] < 256` is DERIVABLE (no axiom — the literal's bytes are literally in range), and a FALSE
  byte-content claim (`b"abc"[0] == 98`) stays UNPROVEN. **Immutability is now respected:** a `bytes`
  element WRITE `b[i] = v` is REJECTED (`PYCSL-SEM-SUBSCRIPT`, unconditional — Python `TypeError:
  'bytes' object does not support item assignment`), never a silent unsound `Array.set`; a `bytearray`
  (mutable) element write stays a sound array mutation. What REMAINS the τ-blessed opaque residual: the
  CONTENT of an *unknown* `bytes` (a PARAMETER — only a user `requires` can bound it), and
  `str↔bytes` encode/decode + deeper `struct`/byte-methods (translational §T.15.5, follow-on). For a
  `bytes` PARAMETER read the value is still a coherent-but-opaque `int` (body `b[i]` == contract `b[i]`;
  distinct indices independent).
- **Class / severity:** WRONG-REPR / 4 (was; now a coherent, type-checking read).
- **Verdict flips (now):**
  - `getting-better/wrong-lowering/wl06_bytes_index_WRONGREPR.py` → **type-checks** (no more
    `subscript_get`); the bare read (no bounds `requires`) is **UNPROVEN** on the honest IndexError
    array-bounds safety VC — a sound fail-closed residual, no longer a broken TYPEERR. Was TYPEERR.
  - With a bounds `requires`, a `bytes`/`bytearray` `b[i]` read → **PROVEN** (`\result == b[i]`,
    concrete-index slot reads) — reference lock `0824.py`.
- **Regression locks (reference corpus):** WL-06 (coherence): `0824.py` (POSITIVE —
  `bytes`/`bytearray` `b[i]` reads under a bounds `requires`, `\result == b[i]`, concrete-index slot
  independence) and `0825.py` (NEGATIVE, `# pycsl-expected: FAIL` — a false byte-content conflation
  `b[0]` claimed `== b[1]`, must stay UNPROVEN). WL-06b (byte content):
  `0835.py` (POSITIVE — bytes-literal exact content `b"abc"[0]==97`/`[1]==98`, hex `b"\xff"==255`),
  `0836.py` (POSITIVE — byte-RANGE invariant `0 <= b[i] < 256` for a literal), `0837.py` (NEGATIVE
  `# pycsl-expected: FAIL` — false byte-content `b"a"[0]==98`, pinned to Z3 to refute fast over the
  array literal), `0838.py` (NEGATIVE `# pycsl-expected: FAIL` — a `bytes` element WRITE is REJECTED,
  immutability). SMT-feasibility spike `test-suite/corpus/conformance/spikes/wl06b_bytes_content_spike.mlw`
  (byte-literal content read + range invariant + no-over-claim; Valid on Alt-Ergo AND Z3).
- **Emission differential:** the full 704-file `pycsl-reference` corpus emits BYTE-IDENTICALLY
  (verified via `bin/byte-diff-sweep.sh`, before/after — only the two new locks 0824/0825 differ); no
  corpus program has a `bytes`/`bytearray` subscript read or `len(bytes)` → additive. NO new axiom.
- **Deliberate-collapse check:** now DOCUMENTED and, for LITERALS, CLOSED. `τ(bytes)=int†` (the coarse
  `array int` SHAPE) stays τ-blessed; WL-06 repaired the BROKEN subscript/`len` emission and WL-06b
  added faithful byte CONTENT for a `bytes` LITERAL (exact value + range invariant) plus immutability
  rejection — additive on top of the coarse shape. The recorded residual is now narrowed to the CONTENT
  of an *unknown* `bytes` (a parameter) and encode/decode + deeper `struct` (translational §T.15.5).
- **Dedup:** none.

---

## Considered and EXCLUDED (τ-blessed or already-documented — NOT findings)

- **bool = int** — τ-blessed lossless 0/1 injection; false twin UNPROVABLE (`cal_bool_falsetwin`).
- **bare `tuple` = int†**, **bytes/bytearray = int†** (as the coarse array-int *shape*) — τ-blessed
  collapse of the SHAPE (WL-06 fixed the broken subscript emission; WL-06b added faithful byte CONTENT for
  a LITERAL + immutability — additive on the shape, §T.15.7). The unknown-`bytes`-parameter content stays
  the residual.
- **`Dict[str,int]` / `Dict[str,str]` value read** — FAITHFUL (`map string (option ν)`), read-back
  proves (`cal_dict_val_faithful`; probes `p_dict_str_val`/`p_dict_int_val` PROVEN).
- **`float` = real** — FAITHFUL (`p_float` PROVEN); false twin `2.0*3.0==7.0` UNPROVABLE.
- **LOCAL dict / set** — FAITHFUL write-read-back and add-membership (`t_localdict`, `t_localset`).
- **list length vs the 1024 backing (G5)** — NOT a bug; `len` is tracked separately
  (`cal_listlen_faithful` PROVEN, `cal_listlen_falsetwin` UNPROVEN).
- **mixed int/float arithmetic** (`x + 1` on `x: float`) — TYPEERR; documented out-of-scope in the
  τ-table float note. Fail-closed; excluded.
- **nonlinear-div vacuity** — WL-VAC above; documented boundary.
- **`hash(s)` opaque int / decode-string equality** — we-are-getting-better.md #39/#40, OUT OF SCOPE.
- **`**` power → `val py_pow`** — OPAQUE (uninterpreted, sound); no consumer; lowest priority, not
  filed as a finding.

---

## Summary

| severity | count | findings |
|---|---|---|
| UNSOUND (1) | 0 open | ~~WL-01 (floor `//`/`%`, neg divisor)~~ **FIXED**, ~~WL-02 (true `/` → int div)~~ **FIXED** |
| FALSE-GREEN (2) | 0 new | WL-VAC (documented, cross-ref) |
| COLLAPSED-with-consumer (3) | 0 open | ~~WL-03 (Tuple param)~~ **FIXED**, ~~WL-04 (List[str/float] elem)~~ **FIXED** |
| WRONG-REPR (4) | 0 open | ~~WL-05 (dict/set param mut)~~ **FIXED**, ~~WL-06 (bytes index)~~ **FIXED** + ~~WL-06b (bytes-literal CONTENT + immutability)~~ **IMPLEMENTED** |
| OPAQUE (5) | 0 filed | — |

**ALL 6 WL-* findings are FIXED.** WL-01 and WL-02 (both certified FALSE arithmetic — a green proof for
code that computes a different value in CPython) are **FIXED**. WL-03 (Tuple param) and WL-04
(List[str/float] element) — both turned away legitimate faithful-typed programs — are **FIXED**. WL-05
(dict/set param item-mutation, which emitted an inconsistent `ref`/non-`ref` mix) is **FIXED** via a
CLEAN REJECTION (the sound, consistent choice — the aliasing/frame boundary shared with record/list
param mutation). WL-06 (bytes/bytearray subscript `b[i]` emitting a broken `subscript_get` mismatch) is
**FIXED** by routing the read to the native `Array.get` (`len(b)` → `Array.length`) — the emission is
now COHERENT and type-checks. Its follow-on **WL-06b** delivers the tractable core of a faithful `bytes`
value model: a `bytes` LITERAL now carries its REAL byte CONTENT (exact value reads PROVE, the byte-range
invariant `0 <= b[i] < 256` is derivable), and `bytes` IMMUTABILITY is respected (a `bytes` element write
is REJECTED, never silently unsound; `bytearray` stays a sound mutable buffer). The coarse `array int`
shape is KEPT — content faithfulness is additive on top of it. **Remaining follow-on (documented, final
residual):** the CONTENT of an *unknown* `bytes` (a parameter — user `requires` only), and `str↔bytes`
encode/decode + deeper `struct`/byte-methods (translational §T.15.5). Harness + drivers + the Alt-Ergo/Z3
SMT spike are committed and re-runnable.
