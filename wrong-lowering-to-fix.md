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
- **LOCALS / RETURN (noted, out of scope):** a `List[str]` LOCAL and a `-> List[str]` RETURN that go
  through the LIST-LITERAL construction (`a = ["x", "y"]`) still collapse the string ELEMENTS to
  hashed ints (`Array.make 2 (747471683)`), a DISTINCT pre-existing surface (the list-literal
  string-element lowering, not the parameter-element collapse). My param-only change does not touch
  it; the return-ANNOTATION side already types `-> List[str]` as `array string`, so a local-literal
  str list currently mismatches its `array string` return (TYPEERR). Filed as a separate follow-on;
  NOT part of WL-04 (which is the PARAMETER element).
- **Record element (noted):** `List[<record>]` is not yet realized as `array <record>` (would need
  the WL-03 record-synthesis seam threaded to the flat list param); str/float — the two faithful
  scalar leaves and the two repro drivers — are done.
- **Dedup:** none (we-are-getting-better.md #6/#7 are IR-node list attrs in the mirror, a different
  surface).

### WL-05 — dict / set PARAMETER item-mutation emits inconsistent `ref` code
- **Construct / position:** `d[k] = v` (`ArraySet`) on a `Dict[...]`/`Set[...]` *parameter*.
- **Current lowering:** `d := map_update_some !d k v; … Map.get d k` — treats the by-value param
  `(d: map string (option int))` as a mutable `ref` (`d :=`, `!d`) AND then reads bare `d` (not
  `!d`) → `string -> option int but is expected to have type ref 'mu`.
- **Faithful target:** either a clean rejection (param mutation out of scope, as for records/lists),
  or a `ref`-wrapped param with a proper frame — consistently one or the other.
- **Class / severity:** WRONG-REPR / 4 (fail-closed via type-check; no false green).
- **Evidence:** `wl05_dict_param_mut_WRONGREPR.py` → **TYPEERR**. Baseline (NOT a finding):
  `wl05_dict_local_FAITHFUL.py` (LOCAL dict write-read-back) → PROVEN. Detector D5 (consequence) + D2.
- **Deliberate-collapse check:** NO. Only RECORD param mutation (static-ref ‡) and LIST inner
  mutation (nested-list-mutable) are documented out-of-scope; dict/set param mutation is
  undocumented AND emits broken WhyML rather than a clean rejection.
- **Fix direction / effort:** in the emitter, either reject param-dict/set mutation with a clear
  diagnostic, or `ref`-wrap the param and use `!d` uniformly on both write and read. / **S–M**.
- **Dedup:** none.

### WL-06 — `bytes` subscript `b[i]` emits `subscript_get(int,int)` on an `array int` value
- **Construct / position:** `b[i]` on a `bytes`/`bytearray` parameter.
- **Current lowering:** param `b : array int` (bytes coarsens to array-backed), but `b[i]` →
  `val subscript_get (x:int)(i:int):int` applied to `b` → `array int` vs `int` mismatch → TYPEERR.
- **Faithful target:** a byte read `Array.get b i` (the param is already `array int`), or a faithful
  `bytes` model.
- **Class / severity:** WRONG-REPR / 4 (low — borderline vs the τ-blessed `bytes=int†`).
- **Evidence:** `wl06_bytes_index_WRONGREPR.py` → **TYPEERR**. Detector D2.
- **Deliberate-collapse check:** NO — with a caveat. `τ(bytes)=int†` is τ-blessed, but the emission
  is BROKEN (subscript op typed against the wrong param shape), not merely a coarse-but-sound read.
  Recorded because a `bytes[i]` read is un-verifiable AND internally inconsistent. Lowest priority.
- **Dedup:** none.

---

## Considered and EXCLUDED (τ-blessed or already-documented — NOT findings)

- **bool = int** — τ-blessed lossless 0/1 injection; false twin UNPROVABLE (`cal_bool_falsetwin`).
- **bare `tuple` = int†**, **bytes/bytearray = int†** (as the coarse *type*) — τ-blessed collapses
  (WL-06 flags only the *broken subscript emission*, not the coarsening).
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
| WRONG-REPR (4) | 2 | WL-05 (dict/set param mut), WL-06 (bytes index) |
| OPAQUE (5) | 0 filed | — |

**Fix priority:** WL-01 and WL-02 (both certified FALSE arithmetic — a green proof for code that
computes a different value in CPython) are **FIXED**. WL-03 (Tuple param) and WL-04 (List[str/float]
element) — both turned away legitimate faithful-typed programs — are now **FIXED**. Remaining:
WL-05/WL-06 emit broken WhyML (fail-closed). Harness + drivers are committed and re-runnable.
