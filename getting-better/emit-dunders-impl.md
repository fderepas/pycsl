# emit-dunders — implementation plan (Gate P)

Synthesized from `emit-dunders-wall.md` (the report) and `emit-dunders-wall-response.md`
(the INDEPENDENT fable review, verdict **PROCEED-WITH-NAMED-CHANGES**, ten oracle runs).
Written 2026-09-23, gen #31.

---

## 0. What the review changed about the plan

The report's spike had already PASSED (route #218's TRUE twin proves once dunders are
emitted). The review confirmed that with its own runs and then moved four things from
"unmeasured" to "measured and red". The plan below is ordered so that **every one of those
four lands in the same increment as the skip removal**, because the review's verdict is
conditional on exactly that.

One item the review named is ALREADY DONE and is not part of this build: its most important
finding, the `x.__str__()` recognizer that bypassed route #218's frame, was landed
separately as **route #220** with witnesses 1820/1821. It had to be: it is a defect at base,
not a consequence of this build, and shipping it inside a large emitter change would have
buried it.

---

## 1. Make-or-break spike — ALREADY RUN, PASSED, and independently reproduced

Env-var-gated edit in `Module5_IREmitter._should_skip_method` (spike worktree only):

    1815 (`\result == 0`, FALSE of CPython)   FAILED  at base   FAILED  under spike
    1815 twin (`== -7`, TRUE)                 FAILED  at base   SUCCESS under spike

Reviewer's O1 reproduces both lines exactly. **Gate S: PASS.** The refutation exit is not
taken.

## 2. The refutation exits that remain live

This plan keeps a REFUTE branch for each of the two costs the review made concrete. If
either cannot be discharged, the corresponding piece is recorded as a CERTIFIED-BOUNDARY
and the build lands WITHOUT it rather than being ground on:

* **R-A.** If `errors.py::PyCSLError.__str__` and `Module2_Parser.py::_Tok.__repr__` cannot
  be made to TYPE-CHECK (they are Why3 type errors, not proof failures — a `seq string`
  receiving an int field, and a `-> int` declaration over an f-string body), then they take
  an explicit `#@ \trusted` marker: 459 -> 461. That is an HONEST correction rather than a
  regression, because both are currently among the UN-trusted mirror functions
  (`check-untrusted-emitted`'s `EXPECTED_ABSENT` allow-list) while never being emitted at
  all — counted as verified and never verified. **The allow-list entry must go in the same
  commit**, or the plane keeps excusing what is no longer absent.
* **R-B.** If `pycsl_lib/plib::PurePath.__str__`'s `#@ ensures \result >= 0` over
  `return self._path` cannot be discharged, the CONTRACT is wrong (it was never checked
  before) and is weakened to what is true, not the method silenced. If neither is possible,
  `plib` is recorded and the build lands with it red-listed in
  `check-stdlib-modules-verify.py`'s known set.

## 3. The build, in order

1. **`__new__` STAYS SKIPPED.** Review O9: `def __new__(cls) -> "N": return
   object.__new__(cls)` is SUCCESS at base and a Why3 type error under the spike; corpus
   0496 survives only because it has no return annotation. `__new__` is not a method (it is
   a static constructor hook) and UB-7.6 already pins it to the trivial form. So the skip
   predicate becomes "skip `__init__` and `__new__`", not "skip `__init__`".
2. **Remove the dunder skip for everything else** in `_should_skip_method`, with the
   measured note in place of the old docstring's claim.
3. **`0402.py` gains `#@ assigns self._n`** on its `__del__`, AND an expected-FAIL twin
   whose `__del__` sets `self._n = -1` under `class invariant self._n >= 0`. Review O4: that
   twin PROVES at base (the body was invisible) and FAILS under the spike, so the build
   turns `#@ allow_finalizer` from "we ignore your finalizer" into "your finalizer must
   respect the invariant and its frame". The new check deserves the witness.
4. **Lift the route #216 pre-scan refusal** (`PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED` in
   `pycsl.py`) in the SAME increment. Review O6: with the skip removed but the refusal in
   place, 1805 is still refused and no goal is built — §6 of the report ("the Liskov
   obligation becomes CHECKABLE") would ship FALSE. With it lifted,
   `goal sub____len___refines_base` IS built and correctly FAILS. Route #216's record and
   its witnesses must be updated in the same commit, and 1805/1806 re-classified.
5. **`preamble.py:9145-9147`'s comment and the UB-7.2 coupling.** Review O10: no double
   declaration (the symbols differ), but the axiom
   `hash_eq_consistent_h: forall a b. h_eq_ a b -> h_hash_ a = h_hash_ b` now sits beside
   emitted `h____hash__`/`h____eq__` bodies it never mentions, so `--strict-hash-eq-
   consistency` remains a check of nothing while LOOKING like it checks the real methods.
   Minimum: correct the comment (it asserts the skip as its justification). Better: tie the
   goal to the emitted bodies. If the second is a value-model build, record it as a
   follow-on rather than expanding this one.
6. **`__post_init__` JOINS `__new__` ON THE SKIP LIST — spiked, decided.** Review O10 said
   emitting it does NOT close route #150 and adds a failing frame goal to every
   `__post_init__` without `#@ assigns`, which is what the hook is for. The spike settles
   the fork: `@dataclass class D: a: int` with a `__post_init__` setting `self.a = 7`, and
   `use()` returning `D(1).a`, FAILS at base under BOTH `\result == 1` and `== 7` — because
   route #150 already has a DEDICATED mechanism for this hook (`has_post_init150`,
   `post_init_nonrecord150`, `Module5_IREmitter` ~3919) that refuses rather than answering
   wrongly. Emitting the method therefore buys NOTHING measured and costs a failing frame
   goal on every honest dataclass. It is a dataclass hook, not a protocol method, and the
   route that owns it is not this build's.
   REOPENING CAPABILITY, recorded rather than left implicit: if route #150's mechanism is
   ever replaced by a real field-initialisation model, `__post_init__` should be re-examined
   together with it — the two are one question, not two.
7. **The mirror**, per R-A: two `\trusted` markers or two body-typing fixes, plus the
   `check-untrusted-emitted` allow-list edit, plus the whole-file re-proof of exactly the
   mirrors whose EMISSION changed (lesson r: emit base and patched, diff, re-prove the
   difference — 18 of 53 by the report's count, all five dunder-defining files confirmed
   DIFFERENT by the reviewer).
8. **`pycsl_lib`**, per R-B.

## 4. The gate battery (unchanged, driver-verified FRESH)

* fidelity: `check-self-annotate-sync.sh` ∧ `self-annotate-mirror-check.sh` (the latter is
  RED at HEAD with three pre-existing drifted mirrors; the requirement is NO NEW drift,
  measured against a worktree at the base commit, not "green")
* proof: whole-file Why3 for every mirror whose emission moved; `--fun` NEVER substitutes
* corpus inertness under the **M1 discipline**, since this build is deliberately NOT
  byte-inert: the diff must be EXACTLY the 20 files (15 + 5), each adjudicated, and every
  affected program must keep its verdict — with 0402 the single intended exception
* ledger == 3; `\trusted` 459 -> at most 461, and every increment above 459 named
* the 45-plane fast battery, and `--slow` before the window closes
* `bin/check-emitted-function-coverage.py` should reach **0 dropped functions** (reviewer's
  O7 measured exactly that under the spike: base 9 dropped / spike 0)

## 5. What this build does NOT fix, recorded so nobody claims it does

* **Implicit dispatch stays unmodelled.** Review O3: `len(c)`, `a + b`, `a == b`, `g[0]`,
  `if b:`, `str(c)` and bare `with c:` on a user class are all loud Why3 type errors or
  pipeline refusals, in both modes. That is a completeness gap, NOT a soundness hazard —
  the reviewer tried and could not construct a false proof through any of them.
* **The `--fun` plane's own hole.** Review O5: `--fun use` PROVES `\result == 0` for a body
  that writes `self.v = 7` without `#@ assigns`, for ORDINARY methods too (control 1817
  shows it at base). The build merely stops shielding dunders from a pre-existing hole.
  **This needs its own route number and its own repair**; it is not an argument against this
  build, and it must not be quietly absorbed into it.
