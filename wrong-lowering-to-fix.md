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

### WL-01 — Python `//` / `%` on a negative divisor lowered to Why3 Euclidean `div`/`mod`
- **Construct / position:** `BinOp //` and `BinOp %` in a function body, any negative divisor.
- **Current lowering:** `pycsl_div`/`pycsl_mod` with `ensures { result = div x y }` / `= mod x y`
  over `use int.EuclideanDivision`. Guarded only by `requires { y <> 0 }` — the divisor SIGN is
  unrestricted.
- **Faithful target:** Python is FLOORED division (`//` rounds toward −∞; `%` sign follows the
  divisor). A `pycsl_floordiv`/`pycsl_floormod` that matches — e.g. `div`/`mod` corrected by
  `if (mod x y <> 0) && ((x<0) <> (y<0)) then q-1`.
- **Class / severity:** UNSOUND / 1.
- **Evidence:**
  - `getting-better/wrong-lowering/wl01_floordiv_neg_UNSOUND.py` → **PROVEN** the FALSE
    `\result == 4` for `(-7)//(-2)` (CPython = **3**). Detector D3.
  - `wl01_floordiv_neg_TRUE.py` → UNPROVEN the TRUE `== 3`.
  - `wl01_mod_neg_UNSOUND.py` → **PROVEN** the FALSE `\result == 1` for `7 % (-2)` (CPython = **−1**).
- **Deliberate-collapse check:** NO. Not a τ-table row. Translational-reference §T.11 **G1** notes a
  divergence exists — but (a) its example `(-7)//2` is itself WRONG (Euclidean `div(-7,2)==-4`, which
  *agrees* with Python, as `cal_floordiv_pos_faithful` proves), (b) the real divergence (negative
  *divisor*) is un-fenced (no `requires`, no rejection), and (c) the suggested `pycsl_floordiv` fix is
  NOT implemented. So this is a documented-but-live UNSOUND gap, not a sound boundary.
- **Fix direction / effort:** emit floored `pycsl_floordiv`/`pycsl_floormod` (correct `div`/`mod` by
  the sign-of-remainder adjustment); update the contract-side `/`→`div` mapping likewise. / **M**.
- **Dedup:** cross-ref translational-reference G1 (under-characterized; correct the example). Not in
  we-are-getting-better.md.

### WL-02 — Python `/` (TRUE division, returns float) lowered to integer Euclidean `div`
- **Construct / position:** `BinOp /` in a body, integer operands, int-return context.
- **Current lowering:** body `/` → `pycsl_div` (int Euclidean `div`) — the fractional part is dropped.
- **Faithful target:** Python `a / b` is TRUE division → a `float` (`real`). It should lower to a real
  division (`float_div_op : real`) or be rejected when the result is used at `int` type — never
  silently truncated.
- **Class / severity:** UNSOUND / 1.
- **Evidence:** `getting-better/wrong-lowering/wl02_truediv_UNSOUND.py` → **PROVEN** `\result == 2`
  for `5 / 2`, but CPython `5/2 == 2.5` (and `2.5 == 2` is False). Detector D3. (The faithful-typed
  variant `-> float` fail-closes with a real-vs-int TYPEERR — see the driver header — so only the
  int-return path is unsound.)
- **Deliberate-collapse check:** NO. The concrete-syntax reference documents `/`→Euclidean `div` for
  *contracts*; the body lowering silently does the same, which contradicts Python's core `/`
  semantics. Not a τ-table row.
- **Fix direction / effort:** distinguish `/` (true, → real) from `//` (floor, → int) in the body
  lowering; reject `int`-typed use of `/`. / **M** (interacts with float/int mixing scope).
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

### WL-03 — `Tuple[T1,…]` PARAMETER collapses to bare `int` (opaque `subscript_get`)
- **Construct / position:** a `Tuple[...]`-annotated *parameter* (and field); slot read `t[i]`.
- **Current lowering:** `let f (t: int) …` with `t[i]` → `val subscript_get (x:int)(i:int):int`
  (content-opaque). The faithful `tuple` model is realized ONLY for locally-constructed / returned
  tuples, NOT params/fields (a `Tuple[...]` field goes to `list`→`array int`, static-ref §1.4 line 305).
- **Faithful target:** a per-slot record (as the τ-table's `τ(Tuple[T1,…]) = tuple` claims), or at
  least a slot-typed read so `t[1] : str` for `Tuple[int,str]`.
- **Class / severity:** COLLAPSED-with-consumer / 3 (mixed-slot: WRONG-REPR / 4).
- **Evidence:**
  - `wl03_tuple_param_COLLAPSED.py` (`Tuple[int,str]`, `return t[1]`) → **TYPEERR** (`t[1]` opaque
    `int` at a `string` return). Detector D2.
  - all-int `Tuple[int,int]` param: body `t[0]` is opaque (content UNPROVABLE); a contract-side
    `\result == t[0]` is itself ill-typed (probe `scratch` `p_tuple_ii`).
  - Baseline (NOT a finding): `wl03_tuple_local_FAITHFUL.py` (LOCAL tuple `t[1]==20`) → PROVEN.
- **Deliberate-collapse check:** NO. The τ-table row `τ(Tuple[T1,…]) = tuple` is UNQUALIFIED and
  claims faithfulness; the param/field realization silently diverges to `int`. Not the τ-blessed
  *bare* `tuple`→int† row (that is a separate, recognized annotation).
- **Fix direction / effort:** thread the recognized-`Tuple` slot types through `_param_type_str` /
  the field realization; give a tuple param the same record/slot model as a local. / **M–L**.
- **Dedup:** none in we-are-getting-better.md (all its items are `int`-leaks in the SELF-annotation
  mirror, not the user-facing Tuple-param surface).

### WL-04 — `List[T]` with a faithful non-int element (`List[str]`, `List[float]`) — element read collapses to `int`
- **Construct / position:** element read `a[i]` on a `List[str]`/`List[float]` param at a
  faithfully-typed use site (str/real return).
- **Current lowering:** `let f (a: array int) … : string = a[i]` — `a[i] : int` vs return `: string`
  (resp. `: real`) → internally inconsistent, ill-typed WhyML.
- **Faithful target:** `array string` / `array real` (or `array (seq τ)` as the nested model already
  does for `List[List[…]]`), so `a[i]` reads the faithful element type.
- **Class / severity:** COLLAPSED-with-consumer / 3.
- **Evidence:** `wl04_list_str_elem_COLLAPSED.py` → **TYPEERR**; `wl04_list_float_elem_COLLAPSED.py`
  → **TYPEERR**. Detector D2.
- **Deliberate-collapse check:** NO — with a caveat. The τ-table says `τ(List[T]) = list (element
  type opaque)`, which blesses an *opaque int* element. But that blessing is only sound as a
  *sound-but-uninformative* read; here the surrounding typing is FAITHFUL (return `string`/`real`),
  so the opaque-int element collides and the emitted WhyML does not type-check — a legitimate
  function is REJECTED, not verified nor cleanly diagnosed. The nested campaign already proved the
  faithful element model is achievable (`array (seq τ)`); a flat `List[str]`/`List[float]` should get
  the analogous `array string` / `array real`.
- **Fix direction / effort:** realize a flat `List[τ]` parameter's element as `τ` (not `int`) when
  `τ ∈ {str, float, record, …}`, mirroring the nested-list element analysis one level up. / **M**.
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
| UNSOUND (1) | 2 | WL-01 (floor `//`/`%`, neg divisor), WL-02 (true `/` → int div) |
| FALSE-GREEN (2) | 0 new | WL-VAC (documented, cross-ref) |
| COLLAPSED-with-consumer (3) | 2 | WL-03 (Tuple param), WL-04 (List[str/float] elem) |
| WRONG-REPR (4) | 2 | WL-05 (dict/set param mut), WL-06 (bytes index) |
| OPAQUE (5) | 0 filed | — |

**Fix priority:** WL-01 and WL-02 are top — they certify FALSE arithmetic (a green proof for code
that computes a different value in CPython). WL-03/WL-04 turn away legitimate faithful-typed programs;
WL-05/WL-06 emit broken WhyML (fail-closed). Harness + drivers are committed and re-runnable.
