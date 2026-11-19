# emit-dunders — state-of-the-art report for independent review

**Status when this was written:** 2026-09-23, generation #31 of the PyCSL
self-tcb-reduction driver campaign. The make-or-break spike has PASSED and the blast
radius has been measured. What is wanted from the review is an INDEPENDENT judgement,
backed by at least one oracle run of your own, on whether this build is sound and whether
the measurement below is complete.

---

## 1. The global picture — what PyCSL is, in enough detail to judge this

PyCSL is a deductive verifier for a subset of Python. A `.py` file carries Hoare-logic
contracts in `#@` comments (`requires`, `ensures`, `assigns`, loop invariants, class
invariants, and a large family of policy directives). A six-module pipeline lowers the
program to WhyML, and Why3 discharges the verification conditions with SMT solvers
(alt-ergo, z3).

    Module1 Ingestor -> Module2 Parser -> Module3 Weaver -> Module4/core_ir_semantic
        -> Module5 IREmitter -> Module6 WhyMLTranspiler -> Why3 -> SMT

The project's distinguishing discipline is that **the compiler verifies itself**: a
MIRROR of the compiler's own source lives in `src/self-annotate/src/`, annotated with
PyCSL contracts, and is verified by the compiler. 887 mirror functions are VERBATIM copies
of the live source (an executable fidelity gate checks this); the rest carry an explicit
`#@ \trusted` marker, of which there are exactly 459. Reducing that number honestly — by
converting trusted stubs into verified bodies — is the campaign's headline metric.

Alongside that runs a **soundness-route programme**. A "route" is a demonstrated
UNSOUNDNESS: a program where PyCSL proves a contract that is FALSE of CPython, with the
TRUE twin of the same contract REJECTED. 218 such routes have been found and recorded;
most are closed by a repair or a refusal, each with a corpus witness (an expected-FAIL
file that must fail) and a control (an expected-PASS file that must still prove).

Three executable planes gate every change. They are disjoint on purpose and must never
stand in for one another:

* **Fidelity** — `bin/check-self-annotate-sync.sh` (887 verbatim twins) and
  `bin/self-annotate-mirror-check.sh`.
* **Proof** — `python3 src/pycsl/pycsl.py <file> --import-path src/pycsl`, the WHOLE-FILE
  proof, plus `--fun` for a single function. A `--fun` pass never substitutes for the
  whole-file proof.
* **Corpus inertness** — `bin/byte-diff-sweep.sh` over 1310 `pycsl-reference` and 2199
  `python-reference` programs, compared against a worktree at the base commit. The default
  expectation is ZERO moved emissions; a non-zero diff is allowed only under the "M1
  discipline": the diff is EXACTLY the intended semantic correction, inspected file by
  file, AND every affected program still proves.

Plus a 45-plane battery (`bin/run-soundness-planes.sh`) and an axiom ledger that must stay
at exactly 3.

---

## 2. The wall as first seen

`Module5_IREmitter._should_skip_method` drops **every dunder** — any method whose name
begins and ends with `__` — before any IR is built:

```python
def _should_skip_method(self, node) -> bool:
    if not self._current_class:
        return False
    if node.name.startswith('__') and node.name.endswith('__'):
        return True
    return False
```

`__init__` is special: it is skipped here but the constructor is synthesized from the
class's `init_body` elsewhere, so it is not lost. Every OTHER dunder is simply absent from
the model.

Three consequences have been measured and recorded in the repository:

**(a) An explicitly-called dunder loses its contract (corpus witness 1800).** Because the
method is not emitted as a `let`, a call `c.__enter__()` becomes a per-call-site abstract
`val` with no `ensures` and (until yesterday) no receiver. The witness's own docstring
called this SOUND — "a contractless `val` is fresh and unconstrained at every call, so the
caller can prove LESS, never more."

**(b) That soundness argument was HALF TRUE, and the other half was route #218.** A
contractless `val` is fresh in what it RETURNS and **pure in what it WRITES**, and purity
is a POSITIVE claim about the whole heap. So

```python
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None: self.v: int = 0
    def __enter__(self) -> int:
        self.v = 7
        return 0

#@ ensures \result == 0
def use() -> int:
    c = C(); before: int = c.v; _r: int = c.__enter__(); after: int = c.v
    return before - after
```

PROVED `\result == 0` while CPython answers **-7**, and the TRUE twin (`== -7`) FAILED.
Route #218 was closed EARLIER TODAY by a partial repair: the skip now records the dropped
body's self-writes and the minted `val` carries `writes { self.v }`, so **a FALSE claim
became an ABSENT one** — both `== 0` and `== -7` now fail. That repair is in the tree this
report is written against.

**(c) A dunder override silently erases a Liskov obligation (route #216).** Under
`--check-behavioral-subtyping`, an overriding method `m` that weakens its contract FAILS
with `goal sub__m_refines_base`. Rename it `__len__` and the tool reports "All contracts
formally proven" over a module whose whole body is `type sub = { }`. A refusal now stops
the lie, but the obligation is still not CHECKABLE.

---

## 3. The deeper truth: is this fundamental, or a modelling choice?

It is a modelling choice, and an old one. Nothing about a dunder is harder to lower than
an ordinary method: the body is ordinary Python, the receiver is ordinary, the contract
syntax is identical. The skip exists because **implicit dispatch** is the hard part —
`len(c)` must find `__len__`, `a + b` must find `__add__`, `with c:` must find
`__enter__`/`__exit__` — and dropping the definitions was the cheap way to avoid promising
a dispatch the emitter does not implement.

But the two halves are separable, and the repository already shows they are:
`_should_skip_method`'s own docstring records that an earlier `@property` skip was removed
and that `@property` getters are now emitted as ordinary nullary methods. The IMPLICIT
dispatch path is independently correct today — measured: the same class with `len(c)`
instead of `c.__len__()` and a `__len__` that writes self **FAILS**, correctly. So the
defect is specific to the EXPLICIT `c.__dunder__(...)` call site, which is exactly where
the contractless `val` is minted.

---

## 4. The spike, and what it decided

**Make-or-break question:** if non-`__init__` dunders are emitted as ordinary methods, does
the caller get the real contract — i.e. does route #218's TRUE twin PROVE?

**Edit (spike only, env-var gated):**

```python
if node.name.startswith('__') and node.name.endswith('__'):
    if os.environ.get("PYCSL_SPIKE_EMIT_DUNDERS") == "1" and node.name != "__init__":
        return False
    return True
```

**Result, run:**

    1815 (\result == 0, FALSE of CPython)   Verification FAILED     <- correct
    1815 twin (\result == -7, TRUE)         Verification SUCCESS    <- the payoff

So the build does what it claims: the model becomes faithful, not merely silent.

---

## 5. The blast radius, measured in full

Two whole-corpus emission sweeps, base vs spike, both emitted fresh:

| corpus | files | MOVED | GONE | APPEARED |
|---|---|---|---|---|
| `pycsl-reference` | 1310 | **15** | 0 | 0 |
| `python-reference` | 2199 | **5** | 0 | 0 |

The fifteen: `0402 0411 0412 0413 0414 0496 1315 1317 1493 1494 1502 1800 1807 1815 1816`.
The five: `0075 0090 0091 0092 0148`.

**VERDICTS on all twenty, base vs spike, each run through the shipping pipeline with its
own `# pycsl-flags:` — exactly ONE changed:**

    0402.py   exp=PASS   SUCCESS -> FAILED
    (every other file keeps its verdict, including all five route witnesses
     1315/1317/1493/1494/1502 which stay FAILED as their `# pycsl-expected: FAIL` says)

**0402 is not a regression; it is a defect the skip was hiding.** The file is
"UB-7.5: `__del__` with `#@ allow_finalizer` is accepted":

```python
#@ class invariant self._n >= 0
#@ allow_finalizer
class WithFinalizer:
    def __init__(self) -> None: self._n: int = 0
    def __del__(self) -> None:
        self._n = 0          # writes self state, declares no `#@ assigns`
```

Emitted, it becomes `let withfinalizer____del__ (self) : unit ensures { self._n = old
self._n }` over a body that assigns `self._n`. The frame clause is synthesized from the
ABSENT `#@ assigns` (default: assigns nothing) and the body violates it. The honest fix is
one line, `#@ assigns self._n`, which preserves what the file is for.

**The mirror is the expensive half.** Ten non-`__init__` dunders live in five mirror files
(`errors.py::PyCSLError.__str__`; `frontend/pure_ast.py`'s `AST.__repr__`,
`_ABC.__instancecheck__`, `Ellipsis.__new__`, `_Tok.__repr__`, `Comment.__repr__`;
`frontend/Module2_Parser.py::_Tok.__repr__`; `proof2why3/sertop.py`'s
`SertopSession.__enter__`/`__exit__`; `proof2why3/parser.py::Token.__repr__`). Emitting
them moves **18 of 53** mirror emissions — the five that gain a real `let`, and thirteen
more that IMPORT those classes and gain abstract `val` declarations for the new methods.
Each of the eighteen owes a whole-file re-proof. Whether the ten bodies PROVE their
(default, vacuous) contracts is being measured as this is written; any that do not must
receive an explicit `#@ \trusted` marker, which would move the headline count UP from 459
by as many as ten — honestly, but visibly.

`src/pycsl_lib` holds eight more, in five modules
(`json/decoder.py::JSONDecodeError.__reduce__`, `plib::PurePath.__str__`,
`tmpf::NamedTemporaryFile.__enter__`/`__exit__`, `typ::_CallableAlias.__getitem__`/
`__call__`, `warn::catch_warnings.__enter__`/`__exit__`), gated by
`bin/check-stdlib-modules-verify.py`.

---

## 6. The routes and planes this would move

* **Witness 1800's recorded gap closes.** Its docstring claims only what the model carries
  and warns that "a FAIL witness would be an XPASS the day the gap closes". That day is
  this build, so 1800 must be revisited in the same increment.
* **Route #216's Liskov obligation becomes CHECKABLE**, not merely un-lied-about.
* **Route #218's TRUE twin becomes PROVABLE**, upgrading today's "absent claim" to a
  faithful one.
* **`bin/check-emitted-function-coverage.py`** reports 8 dropped functions across 914
  corpus files, ALL dunders, with 0402 carrying a named EXPLAINED entry. The plane's own
  header says "It closes when dunders are emitted."
* **One of the five remaining undemonstrated refusals** is
  `module6_whyml/functions.py:7911` — "... is not among the emitted functions, so the
  Liskov ..." — which exists BECAUSE dunders are dropped. It may become unreachable (a
  reclassification) or newly reachable (a witness). Which of the two is not yet measured.

---

## 7. Honest limits of this report

* The mirror proof results are NOT IN YET. If several of the ten mirror dunders fail to
  prove, the build's visible cost is a rising `\trusted` count, and the trade — ten honest
  markers against a closed unsoundness class — has not been argued here, only named.
* `python-reference` holds exotica this report has not read: `__aenter__`/`__aexit__`
  (async), `__new__`, `__get__`, `__set_name__`. The sweep says their emissions do not
  move or keep their verdicts, but "the emission did not move" is a weaker statement than
  "the construct is modelled correctly", and no one has checked the second.
* **Implicit dispatch is NOT part of this build.** After it, `c.__len__()` carries a
  contract and `len(c)` still does not go through the emitted body. Whether that asymmetry
  creates a NEW way to prove something false is the question this report is least able to
  answer about itself.
* The `#@ allow_finalizer` / UB-7.5 perimeter assumed a `__del__` that was never modelled.
  Emitting `__del__` bodies may interact with that perimeter in ways only 0402 has probed.
* `__post_init__` matches the dunder pattern but is a dataclass hook, not a protocol
  method. It is emitted by this build. Three route-#150 witnesses cover it and keep their
  verdicts, but nobody has asked whether emitting it CLOSES route #150.

---

## 8. What is asked of the review

1. **Run at least one oracle of your own** and cite it: write and prove a `.mlw`, or run
   `python3 src/pycsl/pycsl.py <file>`, or emit with `--no-proof --keep-mlw` and read the
   WhyML, or run a byte-diff. CONFIRM or REFUTE a NAMED factual claim above. A review with
   no oracle run is not acceptable here — the value wanted is a different evidence base,
   not a second opinion on the prose.
2. Say whether the twenty-file blast radius is COMPLETE, or whether a population was not
   swept (the four that matter: the two corpora, the mirror, `src/pycsl_lib`, and the live
   tree itself).
3. Say whether the asymmetry in §7 (explicit call modelled, implicit dispatch not) is a
   soundness hazard, and if so construct the program that shows it.
4. Say whether `#@ assigns self._n` on 0402 is the right repair or a weakening of what that
   test is for.
5. Name anything above that you believe is stated more strongly than its evidence supports.
