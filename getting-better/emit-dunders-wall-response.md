# emit-dunders — independent review (response)

**Reviewer stance.** I did not see the authoring team's reasoning. Every claim below rests on
a run I made myself against the spike worktree at
`/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad/g31/wt-spike`
(HEAD `fa7d4a72`, one commit behind the main checkout's `16e69429`; the spike's only diff
is the env-var gate in `Module5_IREmitter._should_skip_method`), with
`. scratchpad/g29/env.sh` sourced (why3 1.8.2, `PYTHONHASHSEED=0`). "base" means the
worktree with `PYCSL_SPIKE_EMIT_DUNDERS` unset; "spike" means it set to `1`. All probe
programs live under `.../scratchpad/review/` and their raw logs under `.../review/logs/`.

**One disclosed edit inside the spike worktree:** to measure §6's Liskov claim I gated the
route-#216 refusal in `src/pycsl/pycsl.py` (the `raise _PyCSLSemErr216`) on the same env
var, ran 1805, and then reverted the file with `git checkout`. The worktree's only remaining
modification is the report's own `Module5_IREmitter.py` edit. Nothing under
`/home/fabrice/git/pycsl` was edited except this response file.

---

## 0. Verdict

**PROCEED-WITH-NAMED-CHANGES.**

The build does what §4 says it does — I reproduced 1815 and its TRUE twin exactly — and
the corpus blast radius is complete. But four things must land in the same increment, or
the build ships a false green and a stale refusal:

1. **`expressions.py:8739` must be removed or made to defer to the emitted `__str__`.** It
   hardcodes every `x.__str__()` call to a contractless, receiver-less
   `val str_dunder_op () : string`, BEFORE the method-contract transport runs. Under BOTH
   base and spike, a self-writing `__str__` with a declared `#@ assigns self.v` lets the
   caller PROVE `\result == 0` where CPython answers `-7`, and the TRUE twin (`== -7`)
   FAILS (§2, oracle O2). This is route #218 not closed for `__str__`. It is not created
   by the build, but the build claims to make the model "faithful, not merely silent" for
   explicit dunder calls, and for `__str__` it does neither.
2. **The `pycsl.py` route-#216 refusal must be lifted in the same increment**, otherwise
   §6's "Route #216's Liskov obligation becomes CHECKABLE" is false as shipped: with the
   spike edit alone, 1805 is still refused (`PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED`) and no
   goal is built. With the refusal lifted, `goal sub____len___refines_base` IS built and
   FAILS, as it should (§4, oracle O6).
3. **The mirror and `pycsl_lib` costs are not "up to ten `\trusted` markers"; they are two
   Why3 TYPE ERRORS and one unprovable stub contract**, and they were measurable:
   `src/self-annotate/src/errors.py` whole-file goes SUCCESS → FAILED with
   `This expression has type int, but is expected to have type string` at the emitted
   `pycslerror____str__` body (a `seq string` receiving an int field);
   `src/self-annotate/src/frontend/Module2_Parser.py` under the spike fails with
   `This expression has type string, but is expected to have type int` in the emitted
   `_tok____repr__` (declared `: int`, returns an f-string); and
   `src/pycsl_lib/plib/__init__.py` goes SUCCESS → FAILED because `PurePath.__str__`'s
   `#@ ensures \result >= 0` over `return self._path` was never checked before and is
   unprovable. Eight of the ten mirror dunders are ALREADY `\trusted` (they surface as
   `val ... ensures { true }`), and the two that are not BOTH break loudly — so the honest
   ceiling on the headline count is +2, not +10, and both of those two are type errors
   that `\trusted` hides rather than resolves (§5, oracle O8; §6).
4. **A return-annotated trivial `__new__` becomes a loud Why3 type error under the spike**
   (`def __new__(cls) -> "N": return object.__new__(cls)` — PASS at base, type error at
   spike). Corpus 0496 survives only because it lacks the `-> "Holder"` annotation. The
   build should keep skipping `__new__` (it is not a method; UB-7.6 already pins it to the
   trivial form) or special-case it (§5, oracle O9).

Two further findings that are NOT blockers but must be recorded:

* **The `--fun` plane regresses for dunders under the spike, into the class ordinary
  methods are already in.** 1815 stripped of its annotations: `--fun use` FAILS at base
  (the #218 body-derived frame) and PROVES `\result == 0` under the spike (CPython: -7).
  The non-dunder control 1817 under `--fun use` PROVES the same false claim at base AND at
  spike — so this is a pre-existing `--fun` hole for every method whose body writes self
  without `#@ assigns`, and the build merely stops shielding dunders from it. It deserves
  its own route number; it is not an argument against this build (§3.3, oracle O5).
* **The build strengthens UB-7.5, it does not weaken it.** A `__del__` that sets
  `self._n = -1` under `class invariant self._n >= 0` PROVES at base (the body was never
  modelled) and FAILS under the spike on the `type invariant` goal. So `#@ assigns self._n`
  on 0402 is the right repair, and 0402 should gain an expected-FAIL twin (§4, oracle O4).

---

## 1. Oracle runs — the evidence base (raw)

Runner: `review/run.sh <file> [flags]` runs
`cd <wt-spike> && timeout 900 python3 src/pycsl/pycsl.py <file> [flags]` once with the
env var unset and once with it set to `1`, and prints the verdict line of each.

### O1 — §4's claim CONFIRMED: 1815 and its TRUE twin

`w1815.py` is a byte copy of `1815_route218_witness_dunder_self_write_is_not_pure.py`;
`w1815_twin.py` is the same file with `#@ ensures \result == 0` → `== -7`.

```
$ review/run.sh review/w1815.py
[base]  w1815.py:      [-] Verification FAILED or INCOMPLETE. Check the solver output.
[spike] w1815.py:      [-] Verification FAILED or INCOMPLETE. Check the solver output.
$ review/run.sh review/w1815_twin.py
[base]  w1815_twin.py: [-] Verification FAILED or INCOMPLETE. Check the solver output.
[spike] w1815_twin.py: [+] Verification SUCCESS! All contracts formally proven.
```

Exactly the report's table. The spike emission (`--no-proof --keep-mlw`) shows the
mechanism, which the report does not describe: the call site does NOT call the emitted
`let`; it mints a per-call `val` with the method's contract COPIED onto it:

```
  val c___enter___0 (self: c) : int
    writes { self.v }
    ensures { (self.v = 7) }
  let c____enter__ (self: c) : int
    ensures  { (self.v = 7) }
  ...
    _r := (c___enter___0 c);
```

This is the same transport every non-dunder method call already uses
(`expressions.py` ~6700-6790, the `_module_method_*` tables). It matters for §3.3 below.

### O2 — REFUTES "route #218 CLOSED" for `__str__`, at base AND spike

`p1b_str_assigns_false.py`:

```python
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def __str__(self) -> str:
        self.v = 7
        return "x"

#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _s: str = c.__str__()
    after: int = c.v
    return before - after
```

CPython: `use() == -7`.

```
$ review/run.sh review/p1b_str_assigns_false.py
[base]  p1b_str_assigns_false.py: [+] Verification SUCCESS! All contracts formally proven.
[spike] p1b_str_assigns_false.py: [+] Verification SUCCESS! All contracts formally proven.
$ review/run.sh review/p1b_str_assigns_true.py        # same file, ensures \result == -7
[base]  p1b_str_assigns_true.py:  [-] Verification FAILED or INCOMPLETE. Check the solver output.
[spike] p1b_str_assigns_true.py:  [-] Verification FAILED or INCOMPLETE. Check the solver output.
```

A FALSE contract proves and its TRUE twin is rejected — the route standard, met in both
modes. The spike WhyML (`review/s_p1.mlw`) shows why:

```
  val str_dunder_op () : string
  let c____str__ (self: c) : string          <- emitted by the spike
  ...
    let _s = ref (str_dunder_op ()) in       <- call site still bypasses it
```

Cause: `src/pycsl/module6_whyml/expressions.py:8735-8743` —

```python
        if (isinstance(func_name, str)
                and (func_name == "__str__" or func_name.endswith(".__str__"))
                and not expr.get("args")):
            self._add_abstract_op("val str_dunder_op () : string")
            return "(str_dunder_op ())"
```

— runs before the dotted-call contract transport and before the #218 `skipped_dunder_writes`
frame (`expressions.py:6849-6866`). Its own comment says "byte-clean (no corpus driver
calls `.__str__()`)", which is why no witness caught it. Without `#@ assigns` the same file
(`p1_str_false.py`) still proves `py_use'vc` postcondition Valid under the spike; the file
as a whole fails only because the emitted `c____str__`'s synthesized frame goal fails.

### O3 — implicit dispatch is a LOUD refusal for every operator I tried, in both modes

Probes (each with a user class defining the dunder with a contract, and a caller using the
implicit form): `len(c)` / `__len__`, `a + b` / `__add__`, `a == b` in a body / `__eq__`,
`g[0]` / `__getitem__`, `if b:` / `__bool__`, `str(c)` / `__str__`, bare `with c:` /
`__enter__`.

```
[base]  p2_len_implicit_false.py: Warnings/Errors from Why3: [-] ... FAILED
        -> This expression has type PyCSL_Program.c @rho, but is expected to have type int
[spike] p2_len_implicit_false.py: same type error
[base]  p2_add.py:      This expression has type PyCSL_Program.v @rho, but is expected to have type int
[base]  p2_eq_body.py:  This expression has type PyCSL_Program.w @rho, but is expected to have type int
[base]  p2_getitem.py:  This expression has type PyCSL_Program.g @rho, but is expected to have type int
[base]  p2_bool.py:     This expression has type PyCSL_Program.b @rho, but is expected to have type int
[base]  p9_str_implicit_false.py: ... but is expected to have type int
[base]  p7_with_bare_false.py: [!] PIPELINE ERROR: [whyml-emit]: a `with` statement ... (ROUTE #38/#39)
```

(spike results identical in kind for all of the above; logs in `review/logs/`). Zero
`Unknown`/`Timeout` results in any of these — they are Why3 type errors or pipeline
refusals, never a proof. The explicit spellings under the spike behave as the build
intends: `p2_getitem_explicit.py` (`g.__getitem__(0)`, `ensures \result == 42`) PROVES,
`p2_len_value_explicit.py` PROVES, both FAIL at base.

### O4 — 0402 and the UB-7.5 perimeter

```
$ review/run.sh review/p3_0402_base.py                 # byte copy of 0402
[base]  SUCCESS   [spike] FAILED  (Sub-goal postcondition of goal withfinalizer____del__'vc: Unknown (sat))
$ review/run.sh review/p3_0402_assigns.py              # + `#@ assigns self._n` on __del__
[base]  SUCCESS   [spike] SUCCESS
$ review/run.sh review/p3_0402_inv_violate.py          # assigns + body `self._n = -1`
[base]  SUCCESS   [spike] FAILED  (Sub-goal type invariant of goal withfinalizer____del__'vc: Unknown)
```

### O5 — the `--fun` plane

```
$ review/run.sh review/p10_noannot_false.py            # 1815 minus the dunder's #@ lines
[base]  FAILED    [spike] FAILED                        (whole-file)
$ review/run.sh review/p10_noannot_false.py --fun use
[base]  FAILED    [spike] [+] Verification SUCCESS! All contracts formally proven.
$ review/run.sh review/w1817.py --fun use              # byte copy of 1817 (non-dunder `enter`)
[base]  [+] SUCCESS  [spike] [+] SUCCESS
```

### O6 — route #216 under the spike

```
$ review/run.sh review/w1805.py --check-behavioral-subtyping --memory-model hoare
[base]  PIPELINE ERROR ... PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED ... "a DUNDER is not emitted as a function"
[spike] PIPELINE ERROR ... (identical message)
--- after gating the raise in wt-spike/src/pycsl/pycsl.py on the env var (reverted afterwards) ---
[spike] Sub-goal postcondition of goal base____len__'vc.
        Sub-goal postcondition of goal sub____len__'vc.
        Sub-goal goal of goal sub____len___refines_base.   Prover result is: Unknown
        [-] Verification FAILED or INCOMPLETE.
```

### O7 — blast-radius completeness (corpora)

Independent sweep: every corpus file with an indented `def __x__(` other than `__init__`.

```
test-suite/corpus/pycsl-reference:  43 defs in 30 files
test-suite/corpus/python-reference: 16 defs in  9 files
src/self-annotate/src:              10 defs in  5 files
src/pycsl_lib:                       8 defs in  5 files
src/pycsl:                          14 defs in  6 files
```

30 + 9 = 39 dunder-defining corpus files vs the report's 15 + 5 = 20 moved. The 19 others,
emitted base vs spike with `--no-proof --keep-mlw`:

```
0401 0497 0989 1030 1033 1035 1047 1333 1334 1352 1353 1632 1784 0076 0078 0080 0093:
    NO MLW in either mode — PIPELINE ERROR before emission, and the error text is
    byte-identical base vs spike (17/17 "same error").
1805, 1806: DIFFER when run WITHOUT their `# pycsl-flags`; under their own
    `--check-behavioral-subtyping` flag both are refused before emission in both modes.
```

So the twenty-file corpus radius is COMPLETE. The coverage plane on the eight non-FAIL
moved files:

```
$ python3 bin/check-emitted-function-coverage.py --emit-dir review/cov/base
    ZERO-COVERAGE  0402.py   none of 1 function(s) survived: __del__
[*] 8 corpus file(s) compared; 1 ZERO-COVERAGE, 7 partial drop(s), 9 dropped function(s) of which 0 are NOT dunders.
$ python3 bin/check-emitted-function-coverage.py --emit-dir review/cov/spike
[*] 8 corpus file(s) compared; 0 ZERO-COVERAGE, 0 partial drop(s), 0 dropped function(s) of which 0 are NOT dunders.
```

(both runs then REFUSE because the dir holds < 800 files — the plane's own ratchet, correct.)

### O8 — the mirror and `pycsl_lib`, which the report left unmeasured

Emission diff base vs spike, `--import-path src/pycsl --no-proof --keep-mlw`:

```
errors.py:                 DIFFERS (+103 lines)  let pycslerror____str__ (self: pycslerror) : string   <- real body
proof2why3/parser.py:      DIFFERS (+4)          val token____repr__ ... ensures { true }              <- already \trusted
proof2why3/sertop.py:      DIFFERS (+8)          val sertopsession____enter__ / ____exit__ ... { true } <- already \trusted
frontend/Module2_Parser.py DIFFERS (+11)         let _tok____repr__ (self: _tok) : int                  <- real body
frontend/pure_ast.py:      DIFFERS (+24)         val _abc____instancecheck__, _tok____repr__, ast____repr__,
                                                 comment____repr__, ellipsis____new__ ... { true }     <- already \trusted
```

Whole-file proofs:

```
$ python3 src/pycsl/pycsl.py src/self-annotate/src/errors.py --import-path src/pycsl
base:  [+] Verification SUCCESS! All contracts formally proven.
spike: [-] Verification FAILED or INCOMPLETE.
       File ".../.pycsl_g4qzh8b6.mlw", line 51, characters 31-55:
       This expression has type int, but is expected to have type string
       (line 51 = `parts := Seq.snoc !parts self.pycslerror_filename;` inside pycslerror____str__)

$ python3 src/pycsl/pycsl.py src/pycsl_lib/plib/__init__.py
base:  [+] Verification SUCCESS! All contracts formally proven.
spike: [-] Verification FAILED or INCOMPLETE.
       Sub-goal postcondition of goal purepath____str__'vc.  Prover result is: Unknown (sat)
       Sub-goal postcondition of goal path____str__'vc.
       (PurePath.__str__ is `#@ ensures \result >= 0` over `return self._path`, unconstrained)
```

`frontend/Module2_Parser.py` whole-file under the spike was launched in the background;
see §6 for its status at the time of writing.

### O9 — `__new__`

```
$ review/run.sh review/p5_new.py            # def __new__(cls) -> "N": return object.__new__(cls)
[base]  SUCCESS   [spike] This expression has type int, but is expected to have type PyCSL_Program.n
$ review/run.sh review/p5_new_super.py      # same with super().__new__(cls)
[base]  SUCCESS   [spike] same type error
$ review/run.sh review/p5_new_trusted.py    # + #@ \trusted on __new__
[base]  SUCCESS   [spike] SUCCESS
$ review/run.sh review/w0496.py             # corpus 0496: NO return annotation
[base]  SUCCESS   [spike] SUCCESS (with "unused variable result" warning)
```

The trigger is the return annotation; `\trusted` suppresses body emission.

### O10 — `__hash__`/`__eq__` (UB-7.2) and `__post_init__` (route #150)

`p6_hasheq.py` (class with both, `#@ ensures \result == 5` on `__hash__`, caller
`return h.__hash__()`, `ensures \result == 5`): base FAILED, spike SUCCESS. Spike WhyML:

```
  val h___hash___0 () : int
    ensures { (result = 5) }
  (* UB-7.2 — hash/eq for H *)
  val function h_hash_ (x: h) : int
  val function h_eq_ (a: h) (b: h) : bool
  axiom hash_eq_consistent_h: forall a b: h. h_eq_ a b = True -> h_hash_ a = h_hash_ b
  let h____eq__ (self: h) (other: int) : int   ...
  let h____hash__ (self: h) : int              ...
```

No double declaration (different symbol names), but the UB-7.2 axiom/goal now sits beside
emitted bodies it never mentions: under `--strict-hash-eq-consistency` the goal is over the
uninterpreted `h_hash_`/`h_eq_`, not over `h____hash__`/`h____eq__`. Not a new unsoundness
(the axiom constrains symbols the program never uses), but the preamble comment at
`preamble.py:9145-9147` ("Module 5 skips dunders for body emission, so we declare them as
abstract `val` functions here") becomes false, and strict mode remains a check of nothing.

`p4_postinit.py` (`@dataclass` with `__post_init__` setting `self.a = 7`, `D(1).a`):
`ensures \result == 1` FAILS in both modes, `== 7` FAILS in both modes; the spike adds a
failing `d____post_init__'vc` postcondition (the synthesized empty frame vs a body that
writes `self.a`). So emitting `__post_init__` does NOT close route #150 (the TRUE twin still
fails) and every `__post_init__` without `#@ assigns` — which is what the hook is for —
now fails its own frame goal. 1493/1494/1502 are expected-FAIL and mask this.

---

## 2. §8 question 2 — is the twenty-file blast radius complete?

**For the two corpora: yes, and I re-derived it independently** (O7). Every file that
defines a non-`__init__` dunder either moved (20), errors before emission with a
byte-identical error in both modes (17), or is refused under its own flags (2).

**For the mirror, `src/pycsl_lib`, and the live tree: the report counted but did not
measure, and the measurements are red** (O8). The report's "18 of 53 mirror emissions
move" is consistent with what I see (all five dunder-defining mirror files DIFFER), but the
proof outcome — the thing §7 says is "NOT IN YET" — is: `errors.py` becomes a Why3 type
error, `plib` becomes a proof failure. Neither is a blast-radius omission; both are costs
the report priced as "up to ten `\trusted` markers" when the true shape is "two files break,
one loudly, one on a contract nobody had ever checked".

The live tree (`src/pycsl`, 14 dunders in 6 files) is not itself emitted by anything — it
reaches the proof only through the mirror — so "sweeping" it means sweeping the mirror. That
population is therefore covered by the mirror numbers, not missing.

## 3. §8 question 3 — is the explicit/implicit asymmetry a soundness hazard?

**For the operators, no — and I could not construct the program.** Every implicit form I
tried on a user class (`len`, `+`, `==` in a body, `[]`, truthiness, `str()`, bare
`with`) is a loud Why3 type error or a pipeline refusal in both modes (O3), so nothing is
proved about them, true or false. The asymmetry is a completeness gap (the explicit
spelling proves, the implicit one refuses), not a way to prove something false.

**For `__str__`, yes — but the hazard is at the EXPLICIT call site, and it predates the
build.** O2 is the program: a self-writing `__str__` with `#@ assigns self.v`, called as
`c.__str__()`, proves `\result == 0` (CPython -7) and rejects `== -7`, at base and at
spike. The build does not create it; it fails to fix it, and it makes the emitted body and
the call-site lowering DISAGREE (the `let` exists, the call ignores it). This is the
"dunder whose emitted body and whose dispatch lowering disagree" the review brief asked me
to hunt for, and it is one grep away from the build's own site.

**§3.3 — a subtler one the build introduces on the `--fun` plane** (O5). At base the #218
repair frames the minted `val` from the dunder's BODY (over-approximation, sound). Under
the spike the frame comes from the DECLARED `#@ assigns` only, exactly as for ordinary
methods. Whole-file, the emitted `let`'s own frame goal fails and the file is red; under
`--fun use`, only the caller is proved and `\result == 0` goes green for a body that
writes `self.v = 7`. 1817 (the non-dunder control) shows the same `--fun` green at base, so
this is a pre-existing hole in the `--fun` plane for every method, into which the build now
also drops dunders. The report's "a `--fun` pass never substitutes for the whole-file
proof" is the correct policy statement, but this is a demonstrated FALSE proof under a
shipping flag and deserves a route number of its own.

## 4. §8 question 4 — is `#@ assigns self._n` on 0402 the right repair?

**Yes, and the test should also GROW.** 0402's purpose is "UB-7.5: `__del__` with
`#@ allow_finalizer` is accepted". The clause is true of the body and makes the file prove
under the spike (O4). It is not a weakening: it is the first time the `__del__` body is
CHECKED at all. O4's third run is the point — a finalizer that breaks the class invariant
proved at base (the body was invisible) and fails under the spike on the `type invariant`
goal. So the build turns `allow_finalizer` from "we ignore your finalizer" into "your
finalizer must respect the invariant and its frame", which is strictly stronger. The right
increment adds an expected-FAIL twin of 0402 with `self._n = -1`, so that this newly-real
check has a witness.

One caveat worth stating: `allow_finalizer`'s stated hazard is finalizer TIMING
(non-deterministic in CPython), and emitting the body does not model when it runs — no call
site invokes `withfinalizer____del__`. So the perimeter is unchanged in what it does NOT
promise; it only gains a body check.

## 5. §8 question 5 — stated more strongly than the evidence supports

1. **"Route #218 was closed EARLIER TODAY"** (§2b) — not for `__str__` (O2). The closure
   is keyed on the dotted-call path, and `__str__` has its own earlier path.
2. **"Route #216's Liskov obligation becomes CHECKABLE"** (§6) — not with this edit alone;
   the `pycsl.py` pre-scan refusal fires regardless of emission (O6). Checkable only when
   the refusal is also removed, and then the goal builds and correctly fails.
3. **"the honest fix is one line, `#@ assigns self._n`, which preserves what the file is
   for"** (§5) — true, but the sentence undersells it: the file's check was vacuous before
   and is real after (O4).
4. **"any that do not [prove] must receive an explicit `#@ \trusted` marker, which would
   move the headline count UP ... by as many as ten"** (§5) — eight of the ten are already
   `\trusted`; the ceiling is two. And one of the two (`errors.py::__str__`) is not a proof
   failure but a Why3 type error, which `\trusted` hides rather than resolves (O8).
5. **"So the build does what it claims: the model becomes faithful, not merely silent"**
   (§4) — faithful for the dotted-call path; silent-and-wrong for `__str__` (O2); loud
   for `__new__` with a return annotation where it used to be silent-and-right (O9).
6. **"a 45-plane battery"** (§1) vs the branch's own commit `a3ecb04a` ("the second
   all-green 69-plane battery"). I could not resolve the count from
   `bin/run-soundness-planes.sh` by grep and did not run it; recorded as an inconsistency,
   not a finding.
7. **"the emission did not move" for `__aenter__`/`__aexit__`/`__get__`/`__set_name__`**
   (§7) — I confirm it did not move, and the reason is that every `python-reference` file
   defining them (0076, 0078, 0080, 0093) errors before emission in both modes (O7). The
   report's own caution ("weaker than modelled correctly") is right; these constructs are
   simply outside the emitter.

## 6. What I could not measure

* **`frontend/Module2_Parser.py` whole-file proof under the spike** (the second real
  `let`, `_tok____repr__`) returned after this file was first written:

  ```
  spike Module2_Parser.py: [-] Verification FAILED or INCOMPLETE.
  This expression has type string, but is expected to have type int
  ```

  — the same shape as `errors.py`: a Why3 TYPE ERROR in the emitted `_tok____repr__`
  body (declared `: int`, returns an f-string), not a proof failure. So BOTH real mirror
  `let`s break loudly and both need `\trusted` (459 → 461) or a body-typing fix. The
  base-mode proof of this file returned before hand-off:

  ```
  base Module2_Parser.py: [+] Verification SUCCESS! All contracts formally proven.
  ```

  So it is SUCCESS → FAILED (type error), the same shape as `errors.py`.
* **`frontend/pure_ast.py`, `proof2why3/sertop.py`, `proof2why3/parser.py` whole-file
  proofs** — not run. Their new symbols are all `val ... ensures { true }` (already
  `\trusted`), so I expect no change, but "expect" is not a run.
* **The thirteen mirror IMPORTERS that gain abstract `val`s** — not run. The `val`s I saw
  are all `ensures { true }` or contract copies, which cannot make a previously-green file
  red except by a type mismatch of the kind O8 found in `errors.py`; the risk is real and
  unmeasured.
* **`bin/byte-diff-sweep.sh` over the full corpora** — not re-run (I re-derived the moved
  set by a different method, O7, which is the point).
* **The remaining `pycsl_lib` modules** (`json/decoder`, `tmpf`, `typ`, `warn`) — not run;
  `plib` alone was enough to show the gate is not inert.
* **The plane battery count** (45 vs 69) — see §5.6.
* **`__aenter__`/`__aexit__`/`__get__`/`__set_name__` semantics** — cannot be probed; the
  files that define them do not reach emission.

## 7. Named changes for the increment (summary)

1. Delete or subordinate the `str_dunder_op` short-circuit at `expressions.py:8735-8743`
   so `x.__str__()` goes through the same contract transport as every other method; add
   O2's pair as a route witness + TRUE-twin control. (Blocking: a shipping false proof.)
2. Remove the `pycsl.py` route-#216 pre-scan refusal in the same commit; turn 1805 into a
   goal-fails witness (`sub____len___refines_base`), keep 1806/1807/1808 as controls.
3. Keep skipping `__new__` (or `\trusted` it in the population) — UB-7.6 already confines
   it to the trivial allocation and emitting it as a method is a category error.
4. `errors.py::PyCSLError.__str__` → `#@ \trusted` (459 → 460) with the type error named in
   the marker's reason; `plib::PurePath.__str__` → either a provable contract or `\trusted`.
5. 0402: add `#@ assigns self._n` AND an expected-FAIL twin with an invariant-breaking
   finalizer. Update `functions.py:7204`'s "DOES NOT WORK TODAY" advice and
   `preamble.py:9145` / `expressions.py:5531` / `5694` comments that justify themselves by
   "Module 5 skips dunders".
6. Open a route for the `--fun` plane's declared-frame-only `val` (O5), citing 1817 as the
   base-tree witness; it is independent of this build.
7. Decide `__post_init__` explicitly: either exempt it from emission (it is a constructor
   hook already consumed by route #150's `apply_inheritance`) or accept that every
   unannotated hook now fails its frame goal, and say so in the release note.
