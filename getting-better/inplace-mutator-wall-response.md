# W-IPM — independent review of `inplace-mutator-wall.md`

*Reviewer: independent, 2026-10-12, branch `ghost-assign-bc6`. I read only the report, `src/`,
`docs/`, `test-suite/`, `bin/` and the Why3 stdlib. I did not read the backlog, run log, progress
log or wall-lessons. Every number I assert below comes from a command I ran; the commands and
their outputs are in Appendix A. Scratch probes live in `$SCRATCH/ipm-review/` (session scratchpad);
nothing under `src/`, `test-suite/` or `bin/` was touched.*

## 0. Verdict in ten lines

1. The factual core of the report holds. Every refusal site, message and line number checked
   (6/6). Census anchors re-measured: 449 `\trusted` directive lines, 435 stubs in 44 files, 27
   ledger rows. The §2.2 probe matrix reproduces on 8/8 constructs I re-ran.
2. The "only 8 of 86 type-check after erasure" measurement is credible: both rows I re-did by hand
   (`AuditReport.extend`, `ConcurrencyChecker._warn_if_unprotected`) behave exactly as tabulated,
   including the `array int` third blocker on the second.
3. The hand Why3 model is sound and non-vacuous as claimed (9/9 positive goals Valid, the false
   claim not proved, no axiom). Why3 does reject a stale *array* alias and, a point the report did
   not test, also rejects the self-aliasing call `r.extend(r)` ("illegal alias"): fail-closed.
4. The dict-alias danger is **worse than the report says**: a pure-map stale alias does not merely
   "copy silently", it **proves a claim that is false of CPython** (`stale_dict`: `result = None`
   Valid; Python returns `"b"`). Any dict mutator route must land its alias guard first.
5. It is a modelling choice, not a fundamental limit. Agreed.
6. R-C is the right first build, but the make-or-break as written is weak: the mirror stub's
   contract is `ensures True`, the erased body already proves whole-file in 40 s, and the named
   refutation criterion (callers hitting Why3's reset rule) is unmeasurable because every mirror
   caller of `extend` is itself a `\trusted` `pass` stub. §5 gives a sharper spike.
7. A grammar fact the spike must plan around: `\length(other.passes)` is a **parse error**;
   `len(other.passes)` and `\old(\length(self.passes))` parse. The faithful postcondition is
   expressible, but only in that spelling.
8. No listed route is unsound in itself; two become unsound if landed without their guard: dict
   routes (R-A dict part, R-B) without a method-call alias guard; R-C on an `array int` field holding
   erased records if the element is coerced to `int` (length right, contents wrong — a new fail-open
   shape).
9. Count payoff: 1 stub sure, ≤4 realistic, 8 ceiling, out of 435 (≤1.8%). As a TCB lever the wall
   does not justify a large build. As a soundness increment (a faithful model replacing a refusal,
   closing witness 0981) a *small* R-C chain probe is justified.
10. Dominant cross-cutting blocker: the **int-erasure seam** (`string`↔`int`, `array int` for record
    and tuple elements, `Set[str]` params typed `int` in the mirror). My own probes hit it three times
    without looking for it.

---

## 1. Factual claims (a)

| claim in report | how checked | result |
|---|---|---|
| refusal sites `expressions.py:36`, `7818–7829`, `7781–7816`; `statements.py:2852–2866`, `3034–3047`, `538–560`, `1020–1068` with the quoted message heads | read each range | **CONFIRMED** (A.1) |
| 449 directive lines; 435 stubs in 44 files via `all_trusted`; 27 ledger rows `in-place-mutator` | re-ran the grep, called `all_trusted` on every mirror file, grep of the TSV | **CONFIRMED** 449 / 435 in 44 / 27 (A.2) |
| §2.2 matrix: self-field `append` refused (13b) under plain and `@mutable_state`, for `List[str]` and `List[int]`; `extend`/`setdefault` on a field refused (7820); local `pop` refused (7820); local `append` lowered and proved (`Seq.snoc`); `@mutable_state` set `add` lowered with `writes { self.s }` and proved | probes p1–p7, p9 through `pycsl.py` with full proof | **CONFIRMED** 8/8 (A.3). Note: witness 0981's docstring says a faithful `@mutable_state` list-field arm exists; it exists only for `pyval` seq fields (K1). The report is right, the docstring is loose. |
| no `Array.append`/`array_append`/`resize` anywhere in `module6_whyml/` | grep per file | **CONFIRMED** 0 hits in 18 files (A.4) |
| `AuditReport.extend`: first blocker is the 7820 guard; L3TC-OK after erasing the three sites; the mirror proof is "cheap" | scratch copy of the mirror, stub un-trusted with the verbatim live body, then with the three sites erased to `None`; `--no-proof`; then full proof | **CONFIRMED**: live → 7820 refusal (1.1 s); erased → `L3-tc ✓` (1.6 s); erased full proof → SUCCESS in **40 s** (A.5) |
| `ConcurrencyChecker._warn_if_unprotected`: 13b first blocker, L3TC-OK after erasure, field is `array int` | same method | **CONFIRMED**: live → 13b; erased → `L3-tc ✓`; record `mutable warnings: array int` (A.6). Also visible: the mirror signature is `held: int` where live is `Set[str]`, and `_shared_vars: map string (option int)` — the seam, twice, in one 15-line body |
| hand model: positive goals Valid, false claims not proved, no axiom | my own `spike.mlw` (same shapes, independently written) under alt-ergo and z3 | **CONFIRMED**: 9/9 positive Valid under alt-ergo; z3 Unknown on `self.xs[length old] = v` (matches the report's L39 remark); `bad_append_len` Timeout/Unknown on both (A.7) |
| Why3 rejects a stale alias of a rebound array field | `alias_arr.mlw` | **CONFIRMED**: `This expression prohibits further usage of the variable ys` (A.8) |
| "Dict fields are pure maps and get no such protection, so … would silently copy" | `stale_dict` in `spike.mlw`: `let e = self.d in dict_setdefault self "a" "b"; e "a"` under `ensures { result = None }` | **CONFIRMED and sharpened**: the false claim is **Valid** (alt-ergo 6 steps, z3 917 steps). CPython: `e.get("a")` is `"b"` (A.7, A.9). This is a proved lie, not a silent copy. |
| (not in report) self-aliasing call `r.extend(r)` | `alias_self.mlw` | Why3: `This application creates an illegal alias` → fail-closed. CPython doubles the list (len 4) (A.8, A.9) |
| Why3 stdlib `Array.append` is a proved `let` with three `ensures` | `array.mlw:127` of the installed 1.8.2 | **CONFIRMED** (A.4) |
| 86/435 first blocker; 77/7/2 split; the full 8/86 table; the 56-file corpus scan; byte-diff | not re-run (cost). Two of the 8 rows re-measured by hand and agree. | NOT RE-RUN, consistent on the sample |

**Two things the report did not measure that matter for the plan.**

* **Contract grammar.** `\length(other.passes)` → `PyCSL Syntax Error … expected ')' (got OP '.')`.
  `other.passes == other.passes`, `len(other.passes)` and `\old(\length(self.passes))` parse. So
  `#@ ensures \length(self.passes) == \old(\length(self.passes)) + len(other.passes)` is the spelling
  the R-C spike has to use (A.10). Whether `len(<param>.<field>)` *lowers* to `Array.length` rather
  than to an opaque `iter_length` is itself a spike question (see p10 below).
* **The existing K1 `seq hval` field model has no alias protection either.** Probe p10 (`ys = self.ws;
  self.ws.append({...}); return len(ys) - n0` under `ensures \result == 0`, false of Python) is not
  proved, but only because `ys = self.ws` is int-erased to `let ys = ref 0` and the later assignment
  is a Why3 type error (`has type seq hval, but is expected to have type int`). It fails closed by
  accident, not by design (A.11). A seq value, unlike an array, has no region, so if that local were
  ever typed `seq hval` the stale alias would prove the false claim exactly like `stale_dict`. This
  deserves a corpus witness now, independent of W-IPM.

## 2. Fundamental or modelling choice? (b)

Modelling choice, as the report says. The evidence is direct: Why3 1.8.2 ships `Array.append` as a
proved program function, `writes` on a field is routine, the spike discharges every shape with no
axiom, and the emitter already does the analogous thing for set fields (`self.s <- map_update_some
self.s v 0` + `writes { self.s }`, p7) and for `pyval` list fields (K1 `Seq.snoc` write-back). The
refusals exist because the generic abstract-op fallback *deletes* the effect; the fix is an emission
arm per (mutator × carrier), nothing deeper.

The only thing with a whiff of the fundamental is **aliasing**: Python collections are reference
objects, PyCSL's maps and seqs are values. Arrays get Why3's region discipline for free; maps and seqs
do not. That is why every dict/seq mutator lowering must be paired with a syntactic alias guard, and
why the guard, not the logic, is the risky part.

## 3. Routes (c)

### 3.1 Existing capability the costing should credit
* `_stmt_seq_mut_params` (`functions.py:85`, `:2195`, `:9656`): a **caller-visible mutable list
  parameter** model already exists — `(p: ref (seq stmt_ir))`, append as `p := Seq.snoc !p v`, with a
  fixpoint that propagates by-reference escape through forwarding callees. It is gated on one element
  type (`stmt_ir`). So R-E's *mechanism* exists; what is "large" is the generalisation to arbitrary
  element types and the corpus blast radius on every list-parameter driver. The report's "large"
  verdict stands but for a different reason than "you need a new container".
* K1 `self.f <- Seq.snoc self.f (pyval-wrap x)` (`statements.py:2883`): the self-field append
  write-back exists for `seq hval` fields. It is **not** a cheaper R-C: `\length` on a seq field is
  ill-typed (report §2.2; the report measured it, I did not re-run). The array rebind is the right
  carrier for `array string` fields precisely because `\length` already lowers to `Array.length`.
* The pinned `val __setdefault` (`generic_fold.py:18790`): reuse it for any dict `setdefault`; the
  inline-match cost lesson is real and should be treated as a hard rule for R-B/R-A-dict.
* `map_update_some` + `writes { self.d }` (p7): the dict/set *store* machinery is in place; dict
  mutators are pure functions over the same carrier. R-B is small, as costed.

### 3.2 Ranking
I agree with the order **R-C → R-A → R-D → R-B → R-E (park)** with these corrections:

* **R-C first, but as a soundness increment, not a count lever.** 1 stub sure (`AuditReport.extend`),
  and that stub's mirror contract is `ensures True`. The honest payoff is: a refusal replaced by a
  faithful model with a visible frame, witness 0981 closed (REFUSED → emitted, false claim not
  proved), and the first `array`-field mutator arm the other list routes can grow from. Cost is
  genuinely small (one arm in the array-local branch at `statements.py:3034`, one in the 7820 fallback
  for `extend`/`sort`, both gated on `self.<f>` with an `array` field type).
* **R-C must refuse, not coerce, on `array int` fields holding erased records** (6 of 9 list-field
  receivers). The array-local arm calls `_coerce_to_int` on the appended value for non-string seqs
  (`statements.py:2925–2928`). If the new field arm inherits that, `self._out.append(PyCSLContract(…))`
  becomes `Array.append self._out (Array.make 1 0)`: the length claim proves, the contents are a lie.
  That is a *new* fail-open shape, strictly worse than today's refusal. Gate the arm on "element
  lowers to the field's element type exactly", else keep the 13b refusal.
* **R-A is a census move, not a TCB move** (44 first-blocker, 2 type-check, 0 clean). Its real cost
  is the alias guard: `statements.py:549` triggers only on `.append`, and its source test
  (`val_ir.get("name") in _array_locals | _seq_locals`) matches only `Var` sources — a `ys = self.xs`
  alias of a *field* is not guarded by the emitter at all (today it is harmless because the field
  mutators are refused; under R-C Why3 catches the array case; under any seq-local model it would
  not). Widen both the trigger set (every length-changing mutator) and the source set (field sources)
  in the same commit as the first R-A arm.
* **R-B and the dict half of R-A carry the `stale_dict` hazard.** The dict alias guard
  (`statements.py:1046`) recognises only store statements (`ArraySet`, `FieldAssign`, …). A
  `MethodCall` mutator through an alias is invisible to it. Landing any dict mutator without adding
  `MethodCall` with name in `_SELF_FIELD_MUTATORS` to that guard reopens route #59 with a proved
  false claim (A.7). This is the one place a listed route is *unsound as described* unless its
  companion guard lands first.
* **R-D is free and should be done on demand**, as the report says. Mirror-only, corpus-inert.
* **R-E stays parked**, but note the `r.extend(r)` finding: Why3's alias rule will refuse any
  call that passes the same record to two mutable parameters, so a parameter route inherits a
  fail-closed behaviour on self-aliasing calls for arrays, and needs an explicit refusal for `ref`
  carriers.

### 3.3 Is any route unsound?
Not as a model. Two are unsound as a *delivery* if the guard is omitted (dict routes) or if element
coercion leaks in (R-C on `array int`). The seq-local carrier used by R-A for `pop`/`extend`/`insert`
has the same no-region property as maps; the list alias guard is its only protection.

## 4. Soundness obligations for any new mutator lowering, with witnesses (d)

| obligation | what it means | pin with |
|---|---|---|
| O1 effect present | post-state of the receiver is a function of (pre-state, args): length law, new-element law, old-elements-preserved law | 0980, 0981, 0982, 0983, 1080, 1081 flip REFUSED → **emitted, false claim NOT proved** (each needs a justification row for `byte-diff-compare.py`); plus one *positive* twin per mutator that proves the true length claim (non-vacuity both ways) |
| O2 frame | `writes { self.f }` / `assigns self.f`; frame-preservation for other fields still emitted; a frame lie (`assigns \nothing` + mutator) must fail | a field-receiver twin of 1081 |
| O3 alias closure | every name bound to the receiver object sees the mutation, or the program is refused | arrays: Why3 reset rule (A.8); maps/seqs: alias guards widened to `MethodCall` mutators and field sources; new witnesses for `e = self.d; self.d.setdefault(…)` and `ys = self.xs; self.xs.extend(…)` (expected: REFUSED) |
| O4 self-aliasing call | `r.extend(r)`, `xs.extend(xs)` | arrays: Why3 "illegal alias" (A.8); `ref`/seq carriers: explicit refusal; witness with Python ground truth len 4 |
| O5 exception triggers | `pop()` on empty → `IndexError`; `pop(k)` no default → `KeyError`; `insert` never raises; `sort` on mixed types raises `TypeError` | `no_exception` witnesses per `pycsl-exception-model` |
| O6 cost | pinned `val`s for `setdefault`/`pop`; no inline `match` on `option` in a loop body | reuse `generic_fold.py:18790`; measure steps on the 8 `program_ir.setdefault` stubs before generalising |
| O7 element fidelity | appended value has the field's element type; no `_coerce_to_int` on a record | witness: `self.out.append(Rec(…))` on a `List[Rec]` field under a contents claim false of Python → must be REFUSED, never proved |
| O8 corpus inertness | byte-diff 0 on every emitted file in both corpora; REFUSED → EMITTED only on the six witnesses | `bin/byte-diff-sweep.sh` + `byte-diff-compare.py --min-files 2000` |
| O9 K1 latent alias | `ys = self.ws` on a `seq hval` field must stay refused by design, not by an int-erasure type error | new witness in the 098x family (A.11) |

## 5. Make-or-break spikes (e)

**S-C (R-C pilot), in this order; each step has a refutation.**
1. Corpus-shaped probe (my `p8_report_extend.py`): `@dataclass Report { passes, failures: List[str] }`,
   `extend(self, other)` with
   `#@ ensures \length(self.passes) == \old(\length(self.passes)) + len(other.passes)` and
   `#@ assigns self.passes, self.failures`. Expect: emitted as
   `self.passes <- Array.append self.passes other.passes` under `writes`, Valid in the portfolio.
   **Refuted if** `len(other.passes)` lowers to an opaque `iter_length` (then the postcondition is
   unprovable and the grammar/lowering of parameter-field length is a prerequisite), or if the arm
   cannot be placed without touching an emitted file.
2. Non-vacuity twin: same body under `ensures \length(self.passes) == \old(\length(self.passes))`.
   **Refuted if** proved.
3. Witness 0981: REFUSED → emitted; its `\length(self.xs) == 2` NOT proved. 0980 (`reverse@self`)
   stays REFUSED unless `reverse` is modelled. **Refuted if** 0981 proves or 0980 moves.
4. Byte-diff 0 on both corpora; `0775`/`0941` (set `add@self`) byte-identical. **Refuted otherwise.**
5. Mirror: un-trust `AuditReport.extend` with the step-1 postcondition (not `ensures True`), fidelity
   plane OK, whole-file proof (expect ≈40 s; the erased body already took 40 s, so this step
   discriminates only if the contract is non-trivial). Drop the "callers hit the reset rule"
   criterion: `audit_both`, the only caller, is a `\trusted` `pass` stub, so nothing can be observed
   there. Replace it by a corpus probe `f(r: Report) -> int: n = len(r.passes); r.extend(other);
   return n` which should emit fine (the local holds an `int`, not the array).
6. Element-fidelity gate (O7): the `array int` twin must be REFUSED. **Refuted if** it emits.

**S-A (R-A pilot), only after S-C lands.** `xs.pop()` on a seq local with the `IndexError` trigger;
0982 flips; `1019`/`1200` still refused after the alias trigger set is widened; a new field-source
alias witness refused.

**S-D (any dict route) — gate, not pilot.** Before the first dict mutator arm: the Python form of
`stale_dict` (`e = self.d; self.d.setdefault("a","b"); return e.get("a")`, claim `\result == None`)
must be REFUSED by the widened guard. **Refuted if** it emits; A.7 shows what it would then prove.

## 6. Does the payoff justify the build? What is the real blocker?

**Count:** no. 1 sure, ≤4 realistic, 8 ceiling, none proved, out of 435. Every route's "clean"
column is ≤3. The report's own §3.5 says so and my two spot-checks agree.

**Soundness:** a small R-C is worth doing on its own terms: it replaces a refusal by a faithful,
axiom-free, Why3-region-protected model, closes 0981, and is corpus-inert by construction if placed
inside the refusal arms. Stop there until the seam moves; do not sweep classes.

**Dominant cross-cutting blocker:** the **int-erasure seam**. Behind the 86, 23 stop at
`string`↔`int`, 38 at other type errors; 6 of 9 list-field receivers are `array int` holding records
or tuples; the mirror's own signatures are already erased (`held: int` for `Set[str]`,
`_shared_vars: map string (option int)`, `ys = self.ws` → `ref 0`). W-IPM is the largest *first*
blocker because the refusal fires before Why3 ever type-checks the body; the seam is the binding
constraint behind it, and record-element typing (`array <record>`) is the specific sub-item that
unlocks the list-field population.

---

## Appendix A — oracle artifacts

All commands run from the repository root after `. scratchpad/g29/env.sh`; `PY` =
`.venv/bin/python3 src/pycsl/pycsl.py … --import-path src/pycsl`; `$S` = `$SCRATCH/ipm-review`.

**A.1 Refusal sites** — `sed -n 30,40p; 7775,7835p src/pycsl/module6_whyml/expressions.py` and
`sed -n 2845,2870p; 3025,3050p; 530,565p; 1015,1070p src/pycsl/module6_whyml/statements.py`.
All six message heads match the report verbatim (`MUTATES its receiver in place…`, `MUTATES an
ARGUMENT in place…`, `in-place `append` to list parameter…`, `appends to the collection in the
field…`, `aliasing a list that is later APPENDED to…`, `aliasing a mutated dict…`). → CONFIRMED.

**A.2 Census anchors**
```
$ grep -rhE '^\s*#@\s*\\trusted\b' src/self-annotate/src --include='*.py' | wc -l
449
$ grep -c 'in-place-mutator' getting-better/trusted-reasons.tsv
27
$ .venv/bin/python3 -c '<load bin/probe-conversion-candidates.py; sum(len(all_trusted(f)) for f in mirror files)>'
stubs 435 files 44
```
→ CONFIRMED.

**A.3 §2.2 matrix probes** (`$S/p1…p9`, `PY <probe> --keep-mlw`, full proof)
```
p1_pl_append    plain  @dataclass  self.xs.append(v)      -> PIPELINE ERROR `self.xs.append(...)` appends to the collection in the field `xs` (13b)
p2_ms_append    @mutable_state     self.xs.append(v)      -> same 13b refusal
p9_ms_intappend @mutable_state     self.ns.append(v) int  -> same 13b refusal
p3_ms_extend    @mutable_state     self.xs.extend([v])    -> `self.xs.extend(...)` MUTATES its receiver in place (7820)
p4_ms_setdefault @mutable_state    self.d.setdefault(k,v) -> 7820
p5_local_pop    xs=[0,7]; x=xs.pop(); ensures \result==7 -> `xs.pop(...)` MUTATES its receiver in place (7820)
p6_local_append xs=[]; xs.append(3); ensures \result==1 -> Valid (3972 steps); SUCCESS.  mlw: `xs := Seq.snoc !xs 3`
p7_ms_sadd      @mutable_state     self.s.add(v)          -> SUCCESS. mlw: `writes { self.s }` / `self.s <- map_update_some self.s v 0`
```
→ CONFIRMED 8/8.

**A.4 Existing capability**
```
$ grep -c 'Array\.append\|array_append\|resize' src/pycsl/module6_whyml/*.py     -> 0 in every file
$ grep -n 'Seq\.snoc' src/pycsl/module6_whyml/statements.py | wc -l               -> 46 (K1 self-field arm at :2882–2917, gated on _pyval_seq_append_targets)
$ grep -n '_stmt_seq_mut_params' src/pycsl/module6_whyml/functions.py             -> :85 `({safe}: ref (seq stmt_ir))`, :2195, :9656 fixpoint builder
$ grep -n 'append' -A3 $(why3 --print-datadir)/stdlib/array.mlw | sed -n 1,5p
127:  let append (a1: array 'a) (a2: array 'a) : array 'a
128:    ensures { length result = length a1 + length a2 }
129:    ensures { forall i. 0 <= i < length a1 -> result[i] = a1[i] }
130:    ensures { forall i. 0 <= i < length a2 -> result[length a1 + i] = a2[i] }
```
→ CONFIRMED (no array-append lowering; stdlib `append` is a proved `let`; a caller-visible
list-param model already exists for `stmt_ir`).

**A.5 `AuditReport.extend` second blocker and proof cost** (`$S/ap_live.py`, `$S/ap_erased.py` =
`src/self-annotate/src/audit_proof.py` with the stub un-trusted; live body verbatim / three sites → `None`)
```
$ PY ap_live.py --no-proof --keep-mlw
[!] PIPELINE ERROR: `self.passes.extend(...)` MUTATES its receiver in place …        real 0m1.137s
$ PY ap_erased.py --no-proof --keep-mlw
[+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks [L3-tc ✓])      real 0m1.641s
$ grep 'type auditreport' ap_erased.mlw
type auditreport = { mutable passes: array string; mutable failures: array string; mutable skips: array string }
$ PY ap_erased.py            (full proof)
[+] Verification SUCCESS! All contracts formally proven.                              real 0m39.989s
```
→ CONFIRMED (first blocker 7820; L3TC-OK after erasure; fields `array string`; whole-file proof 40 s).

**A.6 `ConcurrencyChecker._warn_if_unprotected`** (`$S/cc_live.py`, `$S/cc_erased.py`)
```
cc_live   -> PIPELINE ERROR `self.warnings.append(...)` appends to the collection in the field `warnings` (13b)
cc_erased -> [+] Verification SUCCESS (--no-proof … [L3-tc ✓])
type concurrencychecker = { …; mutable warnings: array int; …; mutable _shared_vars: map string (option int); … }
mirror signature: held: int   (live: held: Set[str])
```
→ CONFIRMED (incl. the `array int` third blocker and the seam).

**A.7 Hand model `$S/spike.mlw`** (`why3 prove -a split_vc -P alt-ergo -t 30`; `-P z3 -t 10`)
```
list_append'vc   : Array creation size V | Postcondition (length) V | (self.xs[length old] = v) V (z3: Unknown) | (old elements) V
report_extend'vc : length passes V | length failures V | old passes preserved V
caller_append'vc : length 3 /\ self.xs[2] = "z"   V
bad_append_len'vc: ensures { length self.xs = length (old self.xs) }   alt-ergo Timeout (30 s) / z3 Unknown   <- NOT proved (false of Python)
stale_dict'vc    : requires { self.d "a" = None } ensures { result = None }
                   body: let e = self.d in dict_setdefault self "a" "b"; e "a"
                   alt-ergo Valid (6 steps) / z3 Valid (917 steps)                                   <- PROVED, and FALSE of Python
```
→ CONFIRMED positive/non-vacuity claims; dict-alias claim CONFIRMED and sharpened (proved lie).

**A.8 Aliasing** (`$S/alias_arr.mlw`, `$S/alias_self.mlw`, `why3 prove -P alt-ergo -t 5`)
```
alias_arr : let stale (self: c) : int = let ys = self.xs in list_append self "a"; length ys
            -> This expression prohibits further usage of the variable ys or any function that depends on it
alias_self: let self_ext (r: report) : unit requires { length r.passes = 2 } ensures { length r.passes = 4 } = report_extend r r
            -> This application creates an illegal alias
```
→ stale array alias rejected: CONFIRMED. Self-aliasing call rejected: NEW, fail-closed.

**A.9 CPython ground truth** (`python3 -I`)
```
r.extend(r) len: 4
ys = xs; xs.append -> len(ys): 2
e = d; d.setdefault -> e.get('a'): b
```

**A.10 Contract grammar on a parameter field** (`$S/p8_report_extend.py`, one `ensures` at a time)
```
\length(self.passes) >= 0                                    -> parses (stops at 7820 refusal)
\length(other.passes) >= 0                                   -> [parse]: PyCSL Syntax Error … expected ')' (got OP '.')
other.passes == other.passes                                 -> parses
\length(self.passes) >= \length(\old(self.passes))           -> parse error
\length(self.passes) >= \old(\length(self.passes))           -> parses
\length(self.passes) == \old(\length(self.passes)) + len(other.passes) -> parses
```
→ NEW: `\length(<param>.<field>)` is inexpressible; `len(<param>.<field>)` is the spelling.

**A.11 K1 stale alias** (`$S/p10_k1_alias.py`: `@mutable_state`, `ws: List[Dict[str, PyVal]]`,
`ys = self.ws; n0 = len(ys); self.ws.append({"a": 1}); return len(ys) - n0`, `ensures \result == 0`)
```
mlw: type c = { mutable ws: seq hval }; val iter_length (x: int) : int; let ys = ref 0 in …; self.ws <- Seq.snoc self.ws (HMap …)
Why3: line 82: This expression has type seq.Seq.seq PyCSL_Program.hval, but is expected to have type int
[-] Verification FAILED or INCOMPLETE
```
→ false claim NOT proved, but via an int-erasure type error, not an alias model. Latent (O9).
