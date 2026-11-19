# genexp-erasure-wall-response.md — independent review

**Verdict: CONFIRM-WITH-CARVE-OUT.**

The wall itself is REAL and I reproduced it from an independent evidence base. But **two of the
report's load-bearing factual claims are FALSE**, and one is an **understatement**:

| report claim | my verdict |
|---|---|
| 8 fully-erased + 4 partially-erased VERIFIED functions; all 8 fully-erased are `IRScanner` | **TRUE** (reproduced exactly) |
| corpus exposure of `any_1`/`all_1` is ZERO | **TRUE** (0 hits over a population of **782**) |
| count is 981, ledger 3 | **TRUE** (981 with the `#@ \trusted` filter; raw grep is 1010, 23 of the delta are docstring mentions) |
| §3/§4: "the SPEC plane already lowers `all(...)` FAITHFULLY to `forall`" | **FALSE — refuted by emission** |
| §6c: `uses_string` is a PURE `let function` and "a loop with a mutable accumulator is not pure", possibly sinking (A) | **FALSE on both halves — refuted by Why3 and by the emitter** |
| §2/§5: "the 9" is the extent of the `any_1` damage | **UNDERSTATED — at least 11 verified functions carry a live `any_1` oracle** |
| §7 make-or-break: can a bounded `any` fold prove a non-vacuous driver, axiom-free? | **YES — oracle run, both provers** |
| §6a/§6b: does an assoc-list-carrier `hval` typecheck and fold? | **YES it typechecks and folds — but ONLY with a hard, measured side-condition the report does not anticipate** |

Everything below is command output I produced. Scratchpad:
`/tmp/claude-1346829620/-home-fabrice-derepas-canonical-com-git-pycsl/9dd932d0-43ec-4eaf-b2b4-3686bbb5f588/scratchpad/rev/`
(`purity1.mlw`, `anyfold.mlw`, `anyfold_MUST_FAIL.mlw`, `evil_crisp.mlw`, `hval_assoc.mlw`,
`hval_nomap.mlw`, `hval_prog.mlw`, `hval_prog_MUSTFAIL.mlw`, `hval_maparm.mlw`, `spec_all*.py`,
`prog_any.py`, `corpus_mlw/`). Why3 1.8.2, Z3 4.13.3, Alt-Ergo 2.6.2. **Every oracle file contains
zero `axiom` declarations** (`grep -c '^ *axiom'` → 0,0,0); nothing here moves the ledger off 3.

---

## 1. ORACLE — §6c, the "cheapest falsifier", falsifies the REPORT, not the plan

The report says the emitter produces a pure `let function` and worries a `ref` accumulator is not
pure. Both halves are wrong.

**(a) Why3 permits it.** A `let function` may contain a `while` loop with local `ref`s — the refs
are allocated *inside*, so the function is still effect-free at its interface (`purity1.mlw`):

```
$ why3 prove -P z3 purity1.mlw
File purity1.mlw:
Goal any_gt10'vc.
Prover result is: Valid (0.01s, 8269 steps).
```

**(b) The emitter does not emit these as `let function` anyway.** From the mirror emission I
generated myself:

```
  let irscanner___check (self: irscanner) (obj: int) : int
  let irscanner__uses_string (self: irscanner) (obj: int) : int
```

Plain `let`, with a `try … raise (Return n) … with Return r -> r end` body — already effectful in
shape. So §6c does **not** sink (A). Note the converse constraint that *is* real and that the
report never states: if the fold's result must be readable back in a **spec** position (`assert`,
`ensures`), the fold must be a **`let function`** (pure) — a plain `let` is not usable in a
specification. My `hval_prog.mlw` hit exactly that: `assert { uses_string t = true }` failed with
`unbound function or predicate symbol 'uses_string'` until I made the group `let rec function`.
That is a design constraint on the implementation, and it is *satisfiable* — see §3.

## 2. ORACLE — §7 make-or-break: the bounded `any`/`all` fold, non-vacuously

`anyfold.mlw`: pure `let function` `any_gt10` / `all_gt10` with a full **iff** postcondition
(`result <-> exists k. 0 <= k < a.length /\ a[k] > 10`), a `ref` accumulator, a loop invariant and a
`variant`; plus three drivers that BUILD a concrete 3-element array and read the answer back.

```
$ why3 prove -P z3 anyfold.mlw
Goal any_gt10'vc.        Valid (0.01s, 10346 steps).
Goal all_gt10'vc.        Valid (0.01s, 10041 steps).
Goal driver_positive'vc. Valid (0.02s, 21849 steps).   (* [1;42;3] -> any=true, all=false *)
Goal driver_evil_twin'vc.Valid (0.01s, 11551 steps).   (* [1;2;3]  -> any=false          *)
Goal driver_all_true'vc. Valid (0.02s, 11916 steps).   (* [11;12;13] -> all=true         *)

$ why3 prove -P alt-ergo anyfold.mlw
… all five Valid (0.04–0.06s)      (* both provers, independently *)
```

**Non-vacuity, two ways.** (i) Flip the evil twin's assertion to the wrong answer
(`anyfold_MUST_FAIL.mlw`): every other goal stays Valid at the same step count and only that one
breaks —

```
Goal driver_evil_twin'vc.  Timeout (10.00s, 7819503 steps).
```

(ii) A crisper, non-timeout falsifier (`evil_crisp.mlw`), taking the iff spec as given and asking
both polarities as ground goals:

```
Goal evil_twin_true_is_FALSE.   Unknown (unknown) (0.02s, 16844 steps)   <- correctly NOT provable
Goal evil_twin_false_is_TRUE.   Valid            (0.01s,  7732 steps)   <- correctly provable
```

**Answer to §7, first half: YES.** A bounded, executable `any`/`all` fold typechecks, proves a full
iff postcondition, discharges a positive AND an evil-twin driver on both provers, uses only
`int.Int`/`ref.Ref`/`array.Array`, and introduces **no axiom**. (A) is feasible. §6c does not sink it.

## 3. ORACLE — §6a/§6b: the assoc-list `hval` DOES work, with one hard condition the report misses

This is where I have news the report does not contain.

**Positive result.** `hval_prog.mlw` — the *full* `IRScanner.uses_string`, faithfully: a mutually
recursive sum `hval / hval_list / hval_pairs` with an association-list carrier `HMapL`, a `size`
measure, four **executable pure `let rec function`s** with `variant` clauses, string keys compared
with the same `str_eq` shape PyCSL already emits, and drivers over a concrete two-level tree with a
nested `{"type": "String"}`:

```
$ why3 prove -P z3 -t 20 hval_prog.mlw
Goal size_pos'vc / size_pos_l'vc / size_pos_p'vc      Valid
Goal uses_string'vc / any_list'vc / any_pairs'vc /
     has_type_string'vc                               Valid
Goal driver_positive'vc    Valid (0.02s,  12194 steps)   (* nested "String" -> true  *)
Goal driver_evil_twin'vc   Valid (0.24s, 705066 steps)   (* "Number" instead -> false *)
```

Anti-vacuity (`hval_prog_MUSTFAIL.mlw`, evil twin asserted `= true`): `High failure (signaled)` —
z3 does not prove it. Zero axioms. **So `.values()` over a `Dict[str,Any]` is NOT the unmodellable
thing the frontier map and §10.3 record — as an association list it is a bounded structural fold
that Why3 proves in a quarter of a second.**

**The condition the report does not anticipate — and it is a blocker for R3 as scoped.** The
report's §4 proposes giving `HMap` an assoc-list carrier *"instead of, or alongside, the map"*.
**"Alongside" does not work.** With the existing `HMap (map string (option hval))` arm re-added to
the same sum — nothing else changed, the fold never even recurses into it —

```
$ why3 prove -P z3 -t 20 hval_maparm.mlw
Goal driver_positive'vc    Valid   (0.02s,  23500 steps)
Goal driver_evil_twin'vc   Timeout (20.00s, 71125526 steps)     <- 100x the steps, no proof
```

and in the logic-level variant (`hval_assoc.mlw`) at 60 s z3 does not merely time out, it dies:
`Goal evil_twin_false. Prover result is: High failure (signaled)`. Dropping the map arm
(`hval_nomap.mlw`) restores it to `Valid (0.47s)`. The **negative** direction is what dies — i.e.
exactly the direction that distinguishes a real proof from a vacuous one.

I isolated the cause enough to rule out the obvious confound: this is **not** lesson (g). Z3 proves
`"Number" <> "String"` in 0.00 s / 487 steps (Alt-Ergo times out, as (g) says). The blocker is the
combination of the infinite-map theory with the ADT in one mutually recursive sum.

**And the map carrier is load-bearing today.** The `hval` theory is emitted into 5 mirror files
(`Module5_IREmitter`, `ir_resolve`, `frontend/__init__`, `pycsl`, `stmt_control_flow`) and there are
real `HMap` constructions and `Map.get` reads in already-converted bodies —
`_collect_final_registry`, `_collect_type_params`, `_collect_typevar_registry`
(`Module5_IREmitter.mlw:1326,1335,1344,1389,1401,1407,1408,1419,1430,1469`), plus a
`map string (option (map string (option hval)))` return type. So R3 is not "add an arm": it is
**replace the carrier and re-lower every existing `hval` consumer**, plus §10.5 re-certification of
Phase2f, plus the mandatory mirror-wide L3-tc sweep (run #4 lesson (a)) across those 5 files.

**Honest "oracle not run":** I did **not** re-run the Rocq/Lean Phase2f certificate against a
carrier-swapped `hval`, and I did not run `Print Assumptions` / `#print axioms`. §6a is therefore
**unresolved by me**. What I can say is only that my Why3 oracles need no axiom; whether the
*certificate* stays axiom-free under a carrier swap is untested and must be a spike gate, not an
assumption.

## 4. Verifying the report's factual claims

### (a) Corpus exposure — TRUE, and I read the population count (lesson (k))

```
$ bash bin/byte-diff-sweep.sh …/corpus_mlw
emitted 782 into …/corpus_mlw (7 jobs)
$ grep -rn 'any_1\|all_1' …/corpus_mlw/ | wc -l
0
$ grep -rln 'isinstance_op' …/corpus_mlw/ | wc -l      # control: the grep does find things
1
$ grep -ln '\bany(\|\ball(' test-suite/corpus/pycsl-reference/*.py
test-suite/corpus/pycsl-reference/0021.py
```

782 emitted vs 782 baseline, one source-level user, zero emitted sites. **Confirmed. A
program-plane `any`/`all` fix is corpus-byte-inert by construction.** (My first sweep attempt
emitted only 543 of 863 before I killed it at 2 min — had I grepped that, I would have reported
"0 hits" off a 30 %-short population. Lesson (k) is not theoretical.)

### (b) "the SPEC plane already lowers `all(...)` to `forall`" — **FALSE.** This is the report's worst error.

`0021.py`'s `all(x >= 0 for x in a)` is a **plain Python `assert` inside `if __name__ ==
"__main__":`** — not a `#@ assert`, not a spec context, and not emitted at all. The full emitted
`0021.mlw` is 20 lines and contains no trace of it. The two `forall`s in that file come from
hand-written `#@ ensures \forall i; …` and `#@ loop invariant \forall j; …` clauses, which have
nothing to do with `all()`.

I then probed the spec plane directly. A genexp in a `#@ assert` does not even parse:

```
$ python3 src/pycsl/pycsl.py --no-proof --no-typecheck --keep-mlw spec_all.py
[parse]: PyCSL Syntax Error around line 12:
assert all(x >= 0 for x in arr)
expected ')' (got NAME 'for')
```

And a non-genexp `all(...)` in a `#@ assert` lowers to **the same unconstrained oracle**:

```
  (* Abstract operations for unsupported Python patterns *)
  val all_1 (a: array int) : bool
  val any_1 (a: array int) : bool

  let g (arr: array int) : unit
  = assert { (all_1 arr) };
    assert { (any_1 arr) };
```

There is exactly one handler (`expressions.py:5392`, `if func_name in ("any","all")`), reached from
every context. **There is no faithful spec-plane lowering, so the report's claimed "existence proof
that the shape is expressible" does not exist.** This cuts both ways: it removes the report's
free-lunch argument, and it *raises* the value of (A), which must now serve both planes. The
program-plane spike reproduces verbatim, including `xs` being dropped:

```
  val any_1 (a: array int) : bool
  let has_big (xs: array int) : int = (if (any_1 (Array.make 1 0)) then 1 else 0)
```

### (c) `bin/check-emitted-vacuity.py` — reports what the report says; findings are REAL, and it UNDER-reports

I emitted all 52 mirror `.mlw` myself (`python3 src/pycsl/pycsl.py <f> --import-path src/pycsl
--no-proof --no-typecheck --keep-mlw`, 52 py → 52 mlw) and ran the probe:

```
[!] emitted-vacuity: 8 VERIFIED function(s) whose emitted body ignores EVERY parameter …
    ir_scanner.mlw::irscanner___check / uses_array_lit / uses_minmax / uses_ord_chr /
    uses_set_card / uses_string / uses_subscript / uses_sum      (erased=['obj'])
[~] … 4 VERIFIED function(s) … SOME parameters …
    Module5_IREmitter.mlw::_collect_class_constants  erased=['field_names']
    expr_ghost_spec_ops.mlw::_handle_mktuple_expr    erased=['lr']
    ir_scanner.mlw::is_recursive                     erased=['obj']
    statements.mlw::_emit_new_ghost_ref              erased=['target']
exit=1
```

8 + 4, all 8 full ones in `IRScanner`. **Matches the report exactly.** ("The 9" = the 8 plus
`is_recursive`, which the probe files as partial because it keeps `name`; the report should say so.)

**Hand-check 1 — `irscanner___check` (claimed fully erased).** The emitted body, read directly out
of `ir_scanner.mlw:214-229`:

```
  let irscanner___check (self: irscanner) (obj: int) : int =
    try
    if ((typeof_op 315) = 4) then begin
      if ((if ((obj_get_1 1342639453) = 20805482) && … then 1 else 0) <> 0) then begin
        raise (Return 1) end
      else begin raise (Return (if (any_1 (Array.make 1 0)) then 1 else 0)) end
    end else begin
      if ((typeof_op 315) = 3) then begin
        raise (Return (if (any_1 (Array.make 1 0)) then 1 else 0)) end
      else begin raise (Return 0) end end
    with Return r -> r end
```

`obj` is the only parameter and appears nowhere. **Real, not a probe artifact.**

**Hand-check 2 — `statements.mlw::_emit_new_ghost_ref`, `target`.** Live body:

```python
declared_refs.add(target); local_refs.add(target)
rest_code = self._stmts_to_whyml(rest, local_refs, declared_refs, indent, in_loop)
```

Emitted (`statements.mlw:264-271`):

```
    let rest_code = ref "" in
    ();
    ();
    rest_code := (self__stmts_to_whyml_5 self rest local_refs declared_refs indent in_loop);
```

Both `Set[str].add` calls are emitted as literal **`()`** — dropped no-ops, and `target` is
consequently unused. **Real, and it is a DIFFERENT defect from the one the report is about**: not
`any`/genexp erasure at all, but a silently-dropped `set.add` on a parameter. Given lesson (h)
(dict params are by-reference and fail-closed; `list.append` on a param silently snapshot-copies),
this is a third member of that family and deserves its own entry. The report treats the 4 partials
as incidental; at least this one is a live-tool faithfulness question.

**Where the probe UNDER-reports (my main addition).** It flags a function only when the emitted
body mentions *none* of the params the live body uses. Two more **verified** functions carry a
live, branch-controlling `any_1 (Array.make 1 0)` and are invisible to it because they use their
*other* parameters:

- `statements.mlw:483` `_handle_fieldassign_stmt` —
  `if (not (any_1 (Array.make 1 0))) then …`, from the live
  `if not any(stripped.startswith(p) for p in map_prefixes):`
- `Module5_IREmitter.mlw:2911` `_union_arm_tag` —
  `if (any_1 (Array.make 1 0)) then raise (…Arm_2_0 (name_of elt)) else raise (…Arm_2_0 "Any")`

So the `any_1` oracle sits on a load-bearing branch in **11 verified functions**, not 9. The report
should say the probe is a **lower bound** on erasure, because it is a whole-function test, not a
per-read test. (The probe's own construction is otherwise sound — the one-line-definition fix and
the string-literal blanking are both present and both necessary; I found no false positive in the
two I checked by hand.)

### Count and ledger

```
$ grep -rhE '#@ +\\trusted' src/self-annotate/src --include=*.py | wc -l   -> 981
$ find src/self-annotate/src -name '*.py' -exec grep -h '\trusted' {} \; | wc -l -> 1010  (23 docstring mentions)
```

981 confirmed. Ledger untouched by anything I ran.

---

## 5. Which route the evidence supports

**Not R1 alone, and not R3 as scoped. Do R2, and gate the 9 rather than re-trusting them.**

- **R2 (build (A)) is justified and now oracle-backed.** §2 settles §7's first half affirmatively on
  two provers, axiom-free, with a working evil twin. §4(a) shows corpus exposure is genuinely zero
  over a verified population of 782, so it is byte-inert by construction. §1 removes the purity
  objection. And §4(b) *strengthens* the case beyond what the report claims: because there is no
  faithful spec-plane lowering either, one fold serves both planes and also repairs
  `#@ assert all(...)`, which today is an unconstrained val in an assert. R2 also unblocks the
  verbatim re-port of `_pattern_has_constructor` (lesson (j) kind 4).

- **R3's `.values()` half is feasible — better than the report expects — but its cost is
  mis-scoped.** §3 proves the assoc-list fold outright. But "alongside the map" is measurably
  unprovable, the map carrier has real consumers in already-converted methods, and §6a (certificate
  axiom-freeness under a carrier swap) is untested. R3 should be re-planned as *carrier replacement
  + re-lowering + re-certification*, and re-costed, before it is authorized.

- **R1 is the wrong instrument.** Re-trusting the 9 converts a *known, gated, measured* vacuity into
  an *ungated assumption* and loses the probe's exit-1 signal. The information is worth more than
  the count. The right move is to keep them enumerated and gated (below), and re-trust only if R2+R3
  are formally declined.

## 6. Mandatory conditions on any implementation

1. **Wire `bin/check-emitted-vacuity.py` into the gate battery now, ahead of any build.** It exits 1
   today; whitelist the 12 known findings **by name** with the reason, so a *new* erasure fails the
   gate. Regardless of route, this must land first. Rationale: without it, R2 can be shipped and the
   9 will still read as "verified".
2. **State in the ledger that the probe is a LOWER BOUND**, and add `_handle_fieldassign_stmt` and
   `_union_arm_tag` to the enumerated vacuity list (§4c). "8 fully erased" is not the exposure.
3. **(A) must carry an iff postcondition, not one direction.** `ensures { result <-> exists … }` /
   `ensures { result <-> forall … }`. A one-directional `->` re-admits vacuity through the back door
   and my `evil_crisp.mlw` asymmetry is exactly what a `->`-only spec would lose.
4. **(A) must be emitted as a pure `let function`** whenever the result can reach a spec position —
   §1(b) shows a plain `let` is unusable in `assert`/`ensures`, and §4(b) shows `all()` *does* occur
   in `#@ assert`. The purity is achievable (local `ref`s; `purity1.mlw` Valid).
5. **(A) must fix BOTH planes in one change,** and the fixture must witness both: a program-position
   `any(genexp)` and a `#@ assert all(genexp)`. Note the latter currently **does not parse** — the
   contract grammar must accept the genexp, which is scope the report omits entirely.
6. **Non-vacuity fixture, positive + evil twin, both provers.** Not a mutation test — lesson (l).
   Reuse the `anyfold.mlw` shape: build a concrete array, read `true` back, and an evil twin that
   reads `false` and that FAILS when asserted wrongly.
7. **For R3 only — a Gate-S spike that MUST precede any emitter edit:** the assoc-list `hval` with
   **all real arms present in one sum**, proving the evil twin under z3 in bounded time. If the
   `HMap (map string (option hval))` arm must stay, this is where R3 dies; `hval_maparm.mlw`
   (Timeout, 71 M steps) and `hval_assoc.mlw` (High failure at 60 s) are the reproductions.
8. **For R3 only — the carrier swap is not additive.** Re-lower `_collect_final_registry`,
   `_collect_type_params`, `_collect_typevar_registry` and the
   `map string (option (map string (option hval)))` return, re-run the **mirror-wide L3-tc sweep**
   over all 5 hval-emitting files (run #4 lesson (a)), and re-run the Phase2f Rocq/Lean cert with
   `Print Assumptions` / `#print axioms` — **§6a is unresolved; I did not run it.**
9. **Alt-Ergo alone is not an acceptable prover for this family** — it cannot prove
   `"Number" <> "String"` (`Timeout (5.00s, 49601 steps)`) where z3 takes 0.00 s. Every gate here
   must be z3-inclusive. (Lesson (g), re-confirmed.)
10. **Separately, not part of this wall:** `Set[str].add(param)` emitting `()`
    (`_emit_new_ghost_ref`) is a live-tool faithfulness bug in the lesson-(h) family and should be
    filed there, not absorbed into the genexp story.

## 7. Corrections the report should take before it is used as a plan

- Delete the §3/§4 claim that the spec plane lowers `all(...)` faithfully. It does not; `0021.py`'s
  `all()` is an unemitted `__main__` runtime assert, and a genexp in `#@ assert` does not parse.
- Delete §6c as a risk. Why3 permits the loop in a `let function`, and the emitter does not use
  `let function` here anyway. Replace it with the real constraint: the fold must be pure *in order
  to be usable in specs*.
- Say "8 fully + 4 partially erased, and at least 2 more verified functions carry a live `any_1`
  oracle"; call the probe a lower bound.
- Re-scope R3 from "change the `hval` ADT" to "replace the `HMap` carrier, re-lower 3+ converted
  methods, re-certify", and attach condition 7 as its make-or-break gate.

**Bottom line: CONFIRM the wall, CONFIRM (A) is buildable (oracle-proven, axiom-free, byte-inert),
REFUTE the report's spec-plane and purity premises, and CARVE OUT R3 pending a single decisive
spike — whether the assoc-list `hval` can prove its evil twin with the map carrier still in the
sum.**
