---
name: pycsl-stdlib-coverage
description: Battle-tested discipline for writing pure-Python standard library implementations that PyCSL can verify. Covers the full workflow from concrete tests through annotations to formal tests, the shared World architecture (one filesystem, one process table, one clock — mirroring the Unix kernel), three-bucket classification (modelled/specified/stubbed), HAPPY confinement for cross-module coherence, and lessons learned from os (fully proven, 0 unproven), re (16/16 VCs), warnings (18/18 body + 3/3 formal VCs), and json (6/6 formal VCs). Use this skill when adding a new stdlib module to src/pycsl_lib/, annotating existing modules, writing formal tests, diagnosing PyCSL proof failures, or applying the convergence-loop ("apply the convergence principle to <module>").
---

# PyCSL Stdlib Coverage

## Purpose and scope

This skill governs the creation and verification of **pure-Python
standard library implementations** that PyCSL can formally verify. The
goal: for every stdlib API that PyCSL uses internally, provide a
verifiable pure-Python model so that PyCSL can eventually verify its
own source code (self-annotation).

The implementations live in `src/pycsl_lib/<module>/` with inline PyCSL
contract annotations. They are **real, runnable Python** — not stubs,
not `pass` bodies. This matters: the implementations are tested
concretely *and* proved formally.

### Everything can be made pure-Python

**No module is inherently un-modelable.** Even modules that interact
with hardware, the OS kernel, the network, or the runtime itself can
be made pure-Python by building an **abstract model** of the
underlying resource — exactly as `src/pycsl_lib/os/UnixInodeFileSystem.py`
models the Unix inode layer with pure-Python arrays and integers.

The pattern:
1. **Identify the resource** — what external state does the module
   read/write? (filesystem, process table, clock, network, memory)
2. **Model it as a Python class** — represent the resource's state as
   fields (lists, dicts, ints). Example: `UnixInodeFileSystem` uses
   arrays for inodes, data blocks, and a free-block bitmap.
3. **Implement APIs against the model** — each stdlib function becomes
   a method that operates on the model's fields, with full contracts.
4. **Prove properties of the model** — because the model is pure
   Python with integer/array operations, PyCSL can verify it.

The model does NOT need to be a perfect replica of the real
implementation. It needs to faithfully capture the **contract-relevant
behavior**: pre/postconditions, state transitions, error conditions.
Abstract away implementation details (caching, buffering, OS-specific
paths) that don't affect the functional contract.

---

## Source of truth — what shapes every stub

A `src/pycsl_lib/` module is not invented; it is **transcribed from Python's
sources of truth**. Two axes decide what a stub must say and do (see
`csl-philosophy` "The source of truth" for the family-wide statement):

- **English — the normative specification.** What the API is *specified*
  to do, including its error conditions:
  - the [Python language reference](https://docs.python.org/3/reference/index.html)
    (semantics of the constructs the module uses), and
  - the [standard library reference](https://docs.python.org/3/library/index.html)
    (the documented behavior of the module itself).
  Mirrored locally under `test-suite/library_reference/`. **This is the
  source of the contracts** — every `ensures` should be a formal shadow
  of a sentence in the library reference (see "Contract-writing rules" below).
- **Execution — the reference implementation.** What the API *actually
  does*: [CPython](https://github.com/python/cpython). It is the ground
  truth for everything the English leaves implementation-defined or
  silent — exact exception types (`KeyError` vs `IndexError`), boundary
  results, iteration/insertion order, what `None`/empty inputs yield.
  **The runnable pure-Python model must agree with CPython** on every
  input the concrete tests exercise.

**How they divide the work on a stub:**
1. Read the **library reference** entry → write the strongest contract it
   justifies (intended behavior, documented exceptions).
2. Where the reference is silent or ambiguous → consult **CPython** for
   the actual behavior, and model *that* (do not guess a convenient
   answer). Pin it with a concrete test against real CPython.
3. Where the reference and CPython **disagree** → that is a finding to
   surface (a doc bug or a CPython quirk), not a coin to flip — record
   the decision and which source you followed, in the module's notes.

This is the **Squeeze Strategy's cornerstone (S0), and the first step of
Extreme Rigor.** A stub is *squeezed* between the two sources of truth:
the library reference bounds its contract from above (the strongest
postcondition the English justifies), CPython bounds it from below (what
actually executes). **Squeezed between the two, the stub has no freedom**
— there is no convenient contract to choose, only the one both force.
That squeeze is *why* a faithful stdlib is even possible: you are not
designing behavior, you are transcribing it. Do this **first**, before
loop invariants or any `\trusted` decision (`csl-from-scratch` §1.5 habit
0; `csl-philosophy` "The source of truth"). The three-bucket
classification, the exception model, and the no-more-int typing all exist
to keep the model honest to these sources.

**Anchor the transcription, and close the loop.** Make the fidelity
*auditable*: anchor each contract to the sentence it transcribes — a
`# cite:` to the reference page and a `# cite:_note:` paraphrase — so a
reader can trace any `ensures` back to its authority (the `os` model
carries one on every syscall). Transcribing is not a one-way trip: the
source of truth is where the proof *ends*, not only where it begins. The
**formal test** (Step 5) re-states the library reference's own promise
over symbolic inputs and discharges it for all of them — the descent into
a faithful model returning, at the top, to the English it came from. A
module is "done" when that loop is closed: spec transcribed into contracts,
contracts proved, and the spec's promise re-proved as a formal test —
**for the WHOLE module's public API, not a sample** (every exported
function/method has a propagating theorem in `formal_<module>.py`; see
Step 5's whole-module coverage rule). A formal test covering only a few of
a module's functions has NOT closed the loop. See `docs/formal-filesystem.md`
(`os` as the worked example).

---

## The World: a shared pure-Python kernel

The Unix kernel maintains **one** coherent state. Our models mirror
that: a single `World` object shared by reference across all modules.
Private copies would let you prove false cross-module theorems.

### World structure

```python
class World:
    clock: ClockModel             # monotonic ticks (Unix §8.4)
    fs: UnixInodeFileSystem       # inodes, data, bitmaps, FDs (Unix §3-§5)
    proc: ProcessState            # pid, cwd, argv, env, umask (Unix §6, §7.2)
```

The World is **region-partitioned by ownership** — `world.fs.*`,
`world.proc.*`, `world.clock.*` each have one owner module, and `sys`,
`io`, `tempfile`, `shutil` are **façades** over the same kernel data
(not modules with private state). The exact ownership table is in
`references/world-architecture.md`.

### Coherence via HAPPY confinement

Cross-module preservation is achieved by **confinement, not per-call
`assigns`**. A HAPPY (High-level Assertion-Producing PYthon
requirement) declares one integrity property per World subsystem:

```python
#@ happy fs_ownership:
#@     protects world.fs.disk, world.fs.inodes, world.fs.bitmaps, world.fs.fd_table
#@     writes outside owner set forbidden
#@     except <fs methods: sys_open, sys_write, _write_inode, ...>

#@ happy proc_ownership:
#@     protects world.proc.cwd_inode, world.proc.environ, world.proc.argv, ...
#@     writes outside owner set forbidden
#@     except <proc methods: chdir, setenv, ...>

#@ happy clock_ownership:
#@     protects world.clock._ticks
#@     writes outside owner set forbidden
#@     except monotonic
```

**What this buys:** because `sys`, `io`, `time`, `subprocess`, and
the pure modules have **no direct write sites** into `world.fs.*`
(all their fs mutation routes through fs methods), the ownership
checks confirm they cannot perturb the fs region. Therefore **any fs
file is preserved across a sys/time/io call with no `assigns` clause
at all** — preservation is a corollary of the ownership invariant.

> **A HAPPY-annotated class is a verified spec-subject, NOT a formal test.** A file whose proof
> shows the method *bodies* satisfy their HAPPY policies / contracts has verified the *spec holds
> of the bodies* — it has NOT exercised the operation's consequence through the public API. To
> also be a formal test it needs a driver that constructs an instance, CALLS the API, and OBSERVES
> the post-state over symbolic inputs (e.g. `formal_bank_transfer.py`'s
> `formal_transfer_moves_money`: `seed → transfer → read balances/audit back → assert`). See the
> three-rule definition in `references/what-is-a-formal-test.md`.

### Flush-through I/O model

`io.StreamModel.write` routes directly to `world.fs.sys_write` with
no private buffer. This means:
- After `io.write(data)`, `os.read(same_fd, n)` sees `data`
- No buffer↔inode divergence — no aliasing problem
- The only fs write site is inside fs (covered by `fs_ownership`)

For the three-bucket classification, the module-by-module bucketing
tables, the Soundness Ledger, the phased implementation order, and the
directory/repo/verification-level architecture, see
`references/world-architecture.md`.

---

## The workflow (battle-tested)

This workflow is one coherent arc — a **descent and a return** — written up end-to-end in
`docs/formal-filesystem.md`, with the `os` module as the worked example. The host module's **source of
truth** (its English spec / POSIX) descends into a **faithful pure-Python model** (no convenient
abstractions — model the real semantics: bytes if the real thing is bytes, partiality kept not
totalized), which you **run concretely** to know it is the *right* model (Step 1), then **annotate
leaf-to-API** so each layer rests on its callees' proved contracts (Steps 2–4), and finally **crown with
a formal test** (Step 5) that re-states the spec's promise over *symbolic* inputs and proves it for every
input at once. The concrete test of Step 1 and the formal test of Step 5 are the **same scenario** — the
formal test is the concrete test with its inputs made universal (the rehearsal, then the proof). Keep the
descent faithful and the return composes.

### Contract-writing rules

These two rules govern HOW you write the postconditions in Step 2 (and
the strongest forms you propagate in Step 5). They are sub-topics of
Step 2, kept here together so the Step 1→5b spine reads straight.

#### Contracts must reflect the English specification

When writing postconditions, **always derive them from the English
documentation in `test-suite/library_reference/`**, not from what
seems "minimal" or "safe" to assert. A contract like
`ensures text == 0 -> \result == 0` (wrapping empty text yields an
empty list) is not "leaking implementation details" — it is a direct
transcription of the documented behavior: *"Returns a list of output
lines"*, and an empty input trivially produces an empty list.

Weakening a postcondition to merely `ensures \result >= 0` when the
English spec says something stronger produces a model that is
technically provable but **unfaithful to the library semantics**.
The whole point of formal verification is to capture *intended
behavior*, not to minimize proof obligations. The RST documentation
is the ground truth; the contract is its formal shadow.

**Rule**: read the English description first, write the strongest
postcondition it justifies, then verify the body satisfies it.
Only weaken if the English is genuinely ambiguous.

#### Always maximise postcondition precision

After writing a contract, **always ask: can I make the postcondition
more strict?** A loose postcondition like `ensures \result >= 0` is
technically true but vacuous — it tells the caller almost nothing.
The goal is to capture the **mathematical essence** of the function.

Example — `gcd(a, b)`:

```python
# BAD: technically true, but says almost nothing
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def gcd(a: int, b: int) -> int: ...

# GOOD: captures what gcd IS
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures (a > 0 or b > 0) ==>
#@   (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int: ...
```

The `\forall k` clause says: no common divisor is larger than the
result. Together with `a % \result == 0 and b % \result == 0`, this
*defines* gcd — the greatest common divisor. A caller can now reason
algebraically about the result, not merely know it is non-negative.

**Checklist for every postcondition:**
1. Does it capture the *exact* return value when possible? (`== f(args)`)
2. Does it capture the *divisibility*, *monotonicity*, or *algebraic
   identity* the function computes?
3. Does it state the *boundary/edge-case* behavior? (e.g., `a == 0 ==> \result == b`)
4. Does it use `\forall` to express *maximality* or *minimality* when
   the function computes an extremum (gcd, max, min, lcm)?
5. Can a caller prove **more** about their own code using this contract?
   If not, the contract is too weak.

### Step 1 — Write a concrete test (scratch)

Write a SCRATCH concrete driver that imports from `src/pycsl_lib/<module>` and exercises all
key functions with concrete values, and run it with `python3` to sanity-check behaviour
before formalizing:

```bash
python3 /tmp/scratch_<module>.py
# PASS: 1 — whitespace matcher
# ...
# PASS: 10 — flags have correct values
```

The KEPT artifact is the FORMAL test (Step 3), named `src/pycsl_lib_test/formal_<module>.py`
(the topical scheme — `formal_re_engine.py`, `formal_json_codec.py`, `formal_os_content.py`,
…); the scratch concrete driver is not committed.

### Step 2 — Annotate the implementation

Add `#@ requires`, `#@ ensures`, `#@ assigns` annotations inline.
Focus on:
- **Preconditions**: input bounds (`pos >= 0`)
- **Postconditions**: return ranges (`\result >= 0 or \result == -1`)
- **Frame conditions**: `assigns \nothing` when pure
- **Class invariants**: field relationships (`self._end >= self._start`)
- **Loop invariants**: needed for while loops in proofs

(Write those postconditions per the "Contract-writing rules" above.)

### Step 3 — Generate WhyML and iterate

```bash
cd /path/to/pycsl
.venv/bin/python3 src/pycsl/pycsl.py --keep-mlw --no-proof src/pycsl_lib/re/__init__.py
```

Check the `.mlw` file. Fix naming issues, type mismatches, missing
imports. Iterate until WhyML type-checks.

### Step 4 — Run body-level proof (if feasible)

```python
# Remove --no-proof to run the full proof
sys.argv = ['pycsl', '--keep-mlw', 'src/pycsl_lib/os/__init__.py']
```

For integer-heavy code (os), this works well — fully proven (0 unproven).
For string-heavy code (re), body-level proof is blocked by tool gaps
(see `references/tool-gaps.md`). Proceed to step 5 regardless.

### Step 5 — Write a formal test

> **DEFINITION — an artifact is a formal test ONLY if all three hold** (the crisp,
> checkable form; see `references/what-is-a-formal-test.md` for examples + anti-patterns):
> 1. **FOR-ALL** — every parameter symbolic, constrained by `#@ requires` (never concrete).
> 2. **CONSEQUENCE** — set up → OPERATE → observe the post-state; assert the *observed effect*,
>    never the call's own return-code (that's vacuous).
> 3. **CALLS THE API** — import + call the public functions; observe through them; never simulate
>    internals.
>
> Miss one and it is NOT a formal test. The subtle miss is a **verified spec-subject**: a class
> annotated with policies/contracts where the proof shows the *bodies* satisfy their own
> pre/postconditions but **no driver constructs an instance, calls the API, and observes a
> post-state** (fails rules 2 & 3). It is a contract proof of the subject, not a consequence test
> — don't file it as `formal_<name>.py` without a consequence driver. A formal test counts only
> when **green AND non-vacuous** (`--check-vacuity`).

Create `src/pycsl_lib_test/formal_<module>.py` with **universally quantified
parameters** — every parameter must be symbolic, never concrete. The
purpose of a formal test is to prove that a property holds **for all
valid inputs**, not just one specific test case.

The body of this step is FIVE distinct rules; each is labelled below so
it is retrievable on its own.

#### Whole-module coverage rule

**Critical rule: the formal test propagates the source of truth across the
WHOLE module — cover EVERY public API symbol, not a sample.** The formal
test is *the* mechanism by which the module's English specification (the
source of truth) is propagated onto its annotations and proved. So it must
re-state and discharge the library-reference promise of **every** public
function/method/class the module exports — each as at least one
universally-quantified theorem, as strong as the faithful model allows (a
real equality/relation where provable; the soundest bound where the
transform is genuinely abstract). **A formal test that exercises only a
couple of a module's functions leaves the rest's specification
unpropagated — the loop is NOT closed and the module is NOT done**, no
matter how green those few theorems are. Concretely: enumerate the module's
public API (the `__init__.py` exports + class methods); every one must
appear in `formal_<module>.py`. Two valid shapes: (a) **one composed
end-to-end scenario** that drives the whole API path — what `os`'s
`formal_os_roundtrip` does over open→write→close→reopen→read; or (b) **one theorem
per API function** when there is no natural composition (e.g. a string or
math module). Either way the acceptance bar is the same: *no documented API
promise left unpropagated*. If a function's faithful promise can't be
proved because the tool can't express it, that is a Step-6 gap (feed it to
the convergence loop), not a licence to omit the function.

#### Universal-quantification rule

**Critical rule: generalize ALL parameters.**

A formal test that uses concrete values is *not* a formal test — it is
just a concrete test re-stated in PyCSL syntax. Compare:

```python
# BAD: concrete test disguised as formal test — proves nothing new
#@ ensures \result == 12
def test_gcd_zero_right() -> int:
    return gcd(12, 0)

# GOOD: universally quantified — proves gcd(n, 0) == n for ALL n
#@ requires n >= 0
#@ requires n < 2147483647
#@ ensures \result == n
def test_gcd_zero_right(n: int) -> int:
    return gcd(n, 0)
```

Each test function:
- Takes **symbolic parameters** with `requires` matching the callee's
  preconditions (plus overflow guards like `< 2147483647` when needed)
- Has an `ensures` clause that is provable solely from the callee's
  postconditions applied to the symbolic arguments
- Returns an expression whose value the `ensures` clause constrains

Why3 generates one weakest-precondition VC per `ensures`, and Alt-Ergo
(then Z3) must return *Valid* on it for **every** integer satisfying the
`requires` — the solver shows the negation unsatisfiable over the whole
symbolic range, not one witness. This is universal quantification — the
essence of formal verification.

See `docs/glossary/formal-test.md` for the concept.

#### Two strengths: totality/safety vs functional content

**Two strengths of a formal-test postcondition — be explicit which you've proved.** A formal test can
assert *totality / safety* — e.g. `#@ ensures \result == 0 or \result == 1` over a driver that returns a
status code: *for every symbolic input the whole composed scenario runs to a well-formed result and
never faults* (no out-of-bounds, no violated precondition, no broken invariant). This is what the `os`
module's `formal_os_roundtrip` proves over all filenames and buffers — the full open→write→close→reopen→read API
cannot be driven into a fault by any file. Or it can assert *functional content* — e.g. `#@ ensures
\result == True` over a round-trip driver that returns `read-back == written`: *the returned value itself
is correct, for all inputs*. Totality is usually reachable first; the content theorem is the deeper
capstone (often proof-cost-bound, not foundation-bound). They are different promises — don't conflate
"the API never faults on any input" with "the API returns the right answer on any input."

#### CONSEQUENCE rule — verify the effect, not the call

**Critical rule: a formal test must verify the operation's CONSEQUENCE, not merely call it.** A formal
test is a *scenario* that exercises the operation's observable EFFECT — never a one-liner that calls the
operation and asserts its own declared return-code/contract. That one-liner is **VACUOUS**: the
operation's `ensures` (e.g. `\result == 0 or \result == -1`) is true *by construction*, so re-asserting it
through a bare call proves NOTHING about what the operation did. The shape of a real test is **set up a
state → observe it → perform the target operation → observe that the state changed as the operation
promises** — the assertion is on the OBSERVED CONSEQUENCE (the post-state), not on the call's own return
value.

This is *why* `os`'s flagship round-trip is the model: `write` data to a file, then **read it back**, and
assert the read-back equals what was written. Writing has a consequence; reading-after-writing checks it —
so the round-trip *proves the write worked*.

BAD — vacuous, do NOT do this (it only re-states `rmdir`'s own return-code disjunction; it never checks the
directory is gone):
```python
#@ ensures \result == 0 or \result == -1
def formal_os_rmdir(name: str) -> int:
    return rmdir(name)            # just calls rmdir — can't tell if anything was removed
```
GOOD — the same syscall, tested by its CONSEQUENCE (**create → check present → rmdir → check absent**):
```python
def formal_os_rmdir_scenario(name: str) -> int:
    mkdir(name)                   # set up: create the directory
    before = access(name)         # observe: it exists
    rc = rmdir(name)              # the target action
    after = access(name)          # observe: it is gone
    #@ ensures before == True and after == False   # the directory was actually removed
    return rc
```
Now the test proves `rmdir` removed the directory — the operation's functional consequence.

By operation kind:
- **Mutating ops** (mkdir / rmdir / unlink / link / rename / write / truncate / chmod …): a
  round-trip/scenario — establish the pre-state, OPERATE, then observe the post-state reflects the change
  (created → present; removed → absent; renamed → old-absent **and** new-present; written → read-back
  equal; truncated → new length).
- **Read-only ops** (stat / access / listdir / getcwd / read …): establish a KNOWN state, then assert the
  observation matches it (after creating N entries, `len(listdir()) == N`; after `mkdir(d)`, `stat(d)`
  reports a directory). The observation is verified against a state YOU constructed, not asserted in a
  vacuum.

A bare return-code assertion (`\result == 0 or -1`) is at best the *totality/safety* strength above (the
call doesn't fault) — keep it only as that, and never mistake it for functional verification. Every
mutating syscall needs a consequence-checking scenario; that is what "the formal test propagates the
source of truth" actually means.

#### `#@ fresh_globals` — surfacing a freshly-imported global's initial state

A formal-test driver runs against the module's shared mutable globals (the World — the os
`_filesystem`, the process table, the clock). Why3 verifies each driver with those globals in an
ARBITRARY state (any prior API sequence could have mutated them), so a driver cannot rely on the
freshly-imported initial state — e.g. that the os fd table is ALL-FREE at entry. When a theorem's
proof genuinely needs that initial state (the canonical case: a free-slot side-condition for the
fd allocator's honest no-ENFILE direction), mark the standalone driver `#@ fresh_globals`:

```python
#@ requires True
#@ ensures \result == 1
#@ fresh_globals          # re-establish each global singleton's constructor post-state at entry
def dup_of_valid_source_is_valid(p: str) -> int:
    fd = open(p, O_CREAT | O_WRONLY, 0o777)   # all-free start ⇒ open + dup both find a free slot
    if fd < 3:
        return 1
    fd2 = dup(fd); close(fd)
    if fd2 >= 3:
        close(fd2); return 1
    return 0
```

`#@ fresh_globals` emits, at the driver's body entry, an `assume` of each module-global singleton's
CONSTRUCTOR post-state (the class `__init__`'s `#@ ensures`, `self` → the global). It is **proof-backed,
not assumed blind**: the transpiler also emits a checked `let g_fresh_init () : C ensures {…} = <ctor
literal>` that PROVES the post-state holds of the freshly constructed global. **Rules:**

- The constructor must carry the post-state as a `#@ ensures` (e.g.
  `#@ ensures \forall k: int; (0 <= k and k < 64) ==> self.fd_open[k] == 0` on
  `UnixInodeFileSystem.__init__`); the directive surfaces exactly that.
- **CONFINED — Module4 rejects it on a method or any callee** (error `PYCSL-SEM-FRESH-GLOBALS`). It is
  sound ONLY on an independent top-level driver that runs on a freshly-imported global; a method runs on
  an arbitrary live `self`/shared global, and a callee inherits its caller's possibly-mutated global —
  assuming the fresh state in either case is unsound.
- It is the SOUND alternative to a blanket-false `requires` (assuming all-free as a precondition is the
  forbidden unsound move — false across a sequence of API calls sharing one global). Used together with
  `#@ propagate_frame` (which carries occupancy across a prior `open`/`dup`), it RETIRES the os
  `fd-resolution-fidelity` reviewer trust by establishing the free-slot side-condition the honest
  conditioned dup/open body theorem needs.

#### CALL-THE-API rule — never simulate

**Critical rule: a formal test CALLS the public API under test — it must NEVER re-implement or simulate the
operation.** The test imports the module's PUBLIC functions and calls them (`mkdir(d)`, then `access(d)`);
it NEVER touches the model's internals (the data structure, private helpers like `_dir_lookup`, raw
`disk[...]` bytes, `sys_*` methods) and NEVER inlines the operation's logic. A test that hand-manipulates
the data structure to "simulate" the syscall — writing the dirent bytes itself, zeroing them, then
re-running the lookup logic inline — proves a **TAUTOLOGY about its own re-implementation, NOT that the API
works**. It is the worst failure mode: a green test that verifies nothing about the module. THE TELL: *if
writing the test required knowing the internal byte layout, you are simulating, not testing.*

BAD — simulates (the exact drift this skill exists to prevent):
```python
def unlink_then_absent(f: str, ino: int) -> int:
    disk = [0]*64
    disk[2] = ord(f[0])          # hand-writes the dirent — re-doing mkdir's job
    disk[2] = 0                  # hand-zeroes it — re-doing unlink's job
    name0 = chr(disk[2]); ...    # inlines _dir_lookup — re-doing access's job
    return found                 # proves the author's re-implementation, not os
```
GOOD — calls the API, observes the consequence through it:
```python
from os import mkdir, unlink, access, F_OK
def unlink_then_absent(f: str) -> int:
    mkdir(f)                     # the REAL syscall
    before = access(f, F_OK)     # the REAL observation
    unlink(f)
    after = access(f, F_OK)
    #@ ensures before == True and after == False
    return 0
```
The formal test sees the module exactly as a *caller* does — through its public surface only. (This is
*why* the test author and the model author must be DIFFERENT agents — see the Convergence Principle: the
**test-agent** is given only the public API + the English spec, never the model internals, so it
physically cannot simulate.)

### Step 5b — Use the axiom registry for inductive properties

Alt-Ergo and Z3 return *Unknown*/*Timeout* on goals that require
induction, cross-function relational reasoning, or uninterpreted
predicates — E-matching cannot manufacture an induction principle. For
these, import cross-validated axioms from the **axiom registry**
(`_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py`).

**Syntax:**
```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
```
Each `#@ proof` directive emits a WhyML `axiom` in the preamble — a
module-level hypothesis in scope for every goal, instantiated via
E-matching like any other quantified fact. The lemma itself is proved
**offline** in Rocq and Lean; no proof-assistant kernel runs during the
`pycsl` proof. Always cite both Rocq and Lean (cross-validation is
required).

**Available axiom families:**

| Prefix | Axioms | Use case |
|--------|--------|----------|
| `Pycsl.Reference.Gcd.*` | 7 (gcd_0, gcd_step, gcd_divides_a/b, gcd_greatest, gcd_result_nonneg/positive) | Euclidean GCD: loop invariant `gcd(x,y)==gcd(a,b)`, divisibility, maximality |
| `Pycsl.Reference.Perm.*` | 2 (permut_refl, rev_permutation) | Permutation properties over `array int` — uninterpreted `permut` predicate |
| `Pycsl.Reference.Json.*` | 1 (mirror_involution) | Inductive properties over recursive `#@ datatype` — structural induction |
| `UnixFs.Bitmap.*` | 1 (bit_and_one_in_zero_one) | Bitwise `(x >> y) & 1 ∈ {0,1}` — Z3 blowup avoidance |
| `UnixFs.Struct.*` | 3 (i1a1, i2, i18 round_trips) | `struct.pack`/`struct.unpack` round-trip identity |

**When to use:**
- Loop invariants with `gcd(x,y) == gcd(a,b)` preservation — needs `gcd_step`
- `\forall k` maximality in GCD postcondition — needs `gcd_greatest`
- `\permutation` on reversed/sorted arrays — needs `rev_permutation`
- Inductive properties over recursive datatypes — needs structural-induction lemma
- Any VC where Alt-Ergo/Z3 returns *Timeout* or *Unknown* within the per-goal budget

**Pattern (GCD flagship, from `test-suite/corpus/pycsl-reference/0342.py`):**
```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof lean Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_greatest
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof lean Pycsl.Reference.Gcd.gcd_result_positive
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == gcd(a, b)
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures (a > 0 or b > 0) ==>
#@   (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    x: int = a
    y: int = b
    #@ loop invariant x >= 0 and y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop variant y
    while y != 0:
        r: int = x % y
        x = y
        y = r
    return x
```

**Trust model:** Each axiom qualname maps to paired Rocq + Lean proofs
in `NNNN.proofs/{rocq,lean}/`, checked **offline** by their respective
kernels — not during the `pycsl` proof. The `audit_proof.py` tool
verifies that both proof assistants accept the lemma and that neither
introduces extraneous axioms beyond the kernel allowlist. A missing or
failing cross-check is a hard error.

### Step 6 — Document tool gaps

Any PyCSL limitation discovered during steps 3–5 is recorded as a
tool-gap requirement. The catalogue of known gaps — stub generation,
tuple results, `assigns`, string params, constant values, default args,
keyword clashes, string ops, class returns — is in
`references/tool-gaps.md`.

---

## The Convergence Principle

Covering the stdlib with formal proofs serves **two purposes at once**, and they are not sequential —
they **converge**:

1. **Annotate the stdlib formally** — re-express each module as a faithful pure-Python model and prove
   it by Hoare logic, exactly as `docs/formal-filesystem.md` does for `os` (this is the workflow,
   Steps 1–6, above).
2. **Debug the PyCSL tool** — the verifier is new, so driving a real module to a *faithful* proof is the
   best stress test there is. Where the model is correct but the tool cannot express or discharge it, the
   proof attempt has found a **tool bug** (Step 6).

Every module proved faithfully exposes tool gaps; fixing those gaps improves the tool; a better tool lets
more of the stdlib be proved. The fixed point is a faithfully-proved module — its formal test propagating
the source of truth across the **WHOLE public API** (Step 5's coverage rule), not a sample — *and* a tool
with no remaining gaps for it.

### The agent loop

A **coordination agent** orchestrates three worker agents — the **stdlib-agent** (builds the `src/pycsl_lib/`
model), the **test-agent** (writes the `src/pycsl_lib_test/` formal test, calling ONLY the public API), and the
**tool-agent** (fixes `src/pycsl/`) — mediated by a **paired traceability document**: a *gap* document
(the problem, from the stdlib-agent OR the test-agent) and a *spec* document (the proposed fix, from the
tool-agent). The model author and the test author are deliberately SEPARATE so the test cannot simulate
the operation it is supposed to call (see Step 5's "call the API, don't simulate" rule + Roles below). Every tool change is auditable back to the stdlib limitation
that motivated it, and the coordination agent approves the **spec** (the plan), not just the gap, before
any edit. Traceability is a key concern, so both documents follow a strict dated naming convention:

- **`DD-HHMM-convergence-gap-N.md`** — written by the stdlib-agent. `DD` = day-of-month, `HH`/`MM` = the
  hour and minute it was created, `N` = the iteration number (1 for the first turn of the loop on this
  module, incremented each turn).
- **`DD-HHMM-convergence-spec-N.md`** — written by the tool-agent in answer, reusing the **same `DD`,
  `HH`, `MM`, and `N`** as the gap document it answers (so the pair is unambiguous and sorts together).
  It opens with a **`STATUS:`** field that drives the handshake through three values:
  **`DRAFT`** (the tool-agent has written its plan) → **`APPROVED`** (the coordination agent has agreed,
  after any edits) → **`DONE`** (the tool-agent has finished and gated the implementation).

```text
   ┌──────────────┐  ①  DD-HHMM-convergence-gap-N.md    ┌───────────────┐
   │ stdlib-agent │ ──────────────── gap ──────────────►│   tool-agent   │
   │ prove <m>;   │                                     │ ② read gap →   │
   │ on a tool    │  ②  DD-HHMM-convergence-spec-N.md    │    write SPEC  │
   │ limit, write │ ◄──────────────  spec  ──────────── │ ④ on approval, │
   │ the GAP doc  │                                     │    fix + gate  │
   └──────▲───────┘        ③ coordination agent         └───────────────┘
          │                  APPROVES the spec doc
          └──────── ⑤ respawn (unblocked; N := N+1) ──────────┘
```

1. The coordination agent **spawns a `stdlib-agent`** to build the `src/pycsl_lib/<module>` MODEL (workflow
   Steps 1–4 — faithful model + `#@` contracts + proved bodies; real WhyML type classes, never an int
   stand-in, never a false postcondition). Then it **spawns a `test-agent`** to write the formal test
   (Step 5, `src/pycsl_lib_test/formal_<module>.py`) that **CALLS ONLY the module's public API** to exercise
   each consequence — the test-agent gets the public API + English spec but NOT the model internals, so it
   cannot simulate.
2. When the `stdlib-agent` (model) OR the `test-agent` (a consequence that won't prove through the API —
   e.g. the syscall's contract exposes no observable post-state) hits something the **tool cannot do**,
   that agent finishes everything it *can* faithfully, then **writes `DD-HHMM-convergence-gap-N.md`** — per
   gap: symptom, minimal reproducer, root cause (`file:line`), the workaround used, and a proposed fix
   (see Step 6 and `10-1732-gap.md` for the shape).
3. The coordination agent **spawns a `tool-agent`** with the gap document. The tool-agent reads it and
   **answers with `DD-HHMM-convergence-spec-N.md`** — its concrete implementation plan, opened with a
   **`STATUS: DRAFT`** field.
4. The coordination agent **reviews and approves the spec** — and approval is *editorial*, not a
   rubber-stamp. It JUDGES the plan and may **add, modify, or remove** parts of it; its goal is to **speed
   up convergence** (cut a risky or needless step, sharpen the gate, redirect the approach). Tool changes
   are the higher-risk half, so the *plan* is gated — and amended — before any edit. When satisfied, the
   coordination agent changes the field to **`STATUS: APPROVED`**.
5. Only on `STATUS: APPROVED` does the tool-agent **implement the spec** and **gate it**: byte-identical
   `.mlw` everywhere else, the affected module/drivers prove, both conformance corpora pass, doc-coherency
   green. It edits *only* `src/pycsl/`, never the stdlib model. When the work is finished and the gate is
   green, the tool-agent changes the field to **`STATUS: DONE`**.
6. The coordination agent **respawns a `stdlib-agent`** to continue from where the previous one stopped,
   now unblocked.

The loop repeats — `N` incrementing each iteration — until a pass produces **no new gaps**.

### Roles (kept strictly separate)

- **coordination agent** — orchestrates the loop and sequences the spawns. Its **approval is editorial**:
  it judges the `DRAFT` spec and may add/modify/remove parts to speed convergence, then sets
  `STATUS: APPROVED`. It never edits source or model code — it edits only the *spec document* (decide,
  amend-the-spec, and dispatch).
- **stdlib-agent** — builds the faithful pure-Python MODEL: edits only `src/pycsl_lib/<module>` (the model + its
  `#@` contracts; workflow Steps 1–4), proves the bodies. It does **NOT** write the formal test. Output: *a
  proved module model and/or a `DD-HHMM-convergence-gap-N.md` gap document*.
- **test-agent** — writes the formal test (workflow Step 5): edits only `src/pycsl_lib_test/formal_<module>.py`,
  and **CALLS ONLY the module's public API** (`mkdir`, `access`, …) to exercise consequences. It is given
  ONLY the public API surface + the English spec (`test-suite/library_reference/`) — **never the model
  internals**, so it physically *cannot* simulate the operation (no `disk[...]`, no `_dir_lookup`, no
  `sys_*`). This separation is the whole point: the model author knows the internals and would be tempted
  to re-do the job in the test; the test-agent can't. Output: *a passing formal test that propagates the
  source of truth THROUGH the real API, and/or a `DD-HHMM-convergence-gap-N.md` gap document* (when an API
  consequence won't prove — e.g. the syscall's contract is return-code-only and exposes no observable
  post-state).
- **tool-agent** — reads the gap document and answers with a `DD-HHMM-convergence-spec-N.md` spec opened
  at `STATUS: DRAFT`; once the coordination agent sets `STATUS: APPROVED`, implements it, gates it, and
  sets `STATUS: DONE`; edits only `src/pycsl/`; output is *a spec document and a gated tool fix*. It never
  weakens the model to dodge a real gap.

### Invocation

Saying **"apply the convergence principle to `<module>`"** spawns the coordination agent on
`src/pycsl_lib/<module>` and runs the loop to its fixed point — e.g. **"apply the convergence principle to
strmod"** targets `src/pycsl_lib/strmod/`.

### Worked precedent

The strmod pass kicked off the loop: a stdlib-agent rebuilt `src/pycsl_lib/strmod/` on real `str` and proved
it (commit `a50bc61`), surfacing three tool gaps it worked around and recorded in `10-1732-gap.md` (the
ad-hoc precursor to the `DD-HHMM-convergence-gap-N.md` convention above — hardcoded `exception Return
int`; `len()` over a string-returning call; the int-`0` default fill for a non-`int` param). The
tool-agent then fixed the first gap — `Return_str` for early returns in string-returning functions
(commit `89b3f55`) — strictly additively (652-driver byte-diff DIFFERS=0). The remaining gaps (the
callee/parameter faithful-type threading) are the next turns; once fixed, a fresh stdlib-agent re-proves
strmod's functions with their *natural* control flow (early returns, omitted defaults) instead of the
workarounds. That is convergence: the module pushed the tool, the tool fix lets the module be pushed
further.

---

## Reference files

Load these on demand — they hold the load-occasionally, look-up content split out of this skill:

- **`references/world-architecture.md`** — consult when placing a new module in the World or checking its
  bucket/status: region-partitioned ownership table, three-bucket classification detail, module-by-module
  bucketing, the Soundness Ledger (TCB), the phased implementation order, and the directory / two-repos /
  two-verification-levels architecture.
- **`references/lessons-and-gotchas.md`** — consult when debugging a specific WhyML/emission gotcha
  (naming clashes, re-export contract loss, constants, string methods, inliner limits, loop patterns,
  exception propagation, `assigns`, tuple results, stuck-proof strategy) or a codec (the serialization
  pack/unpack discipline).
- **`references/tool-gaps.md`** — consult when a body-level proof is blocked, to check whether the blocker
  is a known gap (with its workaround) before treating it as new.
- **`references/status-and-running.md`** — consult when invoking the tool (exact commands, import
  resolution / CWD rules, provers) or picking the next module to cover (per-module current status + the
  phased "what to cover next").

---

## Consolidated heuristics (from `test-supervise-sl` monitoring)

These heuristics were consolidated from the `os` module formal-test fleet runs
(2026-06-22/23), trigger-tested and Gate-S-passed. Full provenance in
`config/skills/pycsl-monitoring/SKILL.md`.

### Co-import trigger for World record emission

When a formal test imports a CLASS from a module that also defines a World
global (e.g. `_filesystem`), co-import at least one FUNCTION that references the
World global in its contract. Importing the class alone does NOT emit the World
record type declaration, causing "unbound symbol" errors in the helper stubs.

### String-returning imported functions cannot assign to locals

For imported functions returning `str`, avoid local variable assignment AND
body-level string `==` — pycsl initializes locals as `ref 0` (int), and assigning
a string return causes a type mismatch. Instead, return the call result directly
and assert the consequence in the `ensures` contract
(`def f(p) -> str: return expanduser(p)` with `ensures \result == p`).

### PyCSL string-op abstract vals (rfind/split/join) → `\abstract` zero-TCB

`str.rfind`, `str.split`, `str.join`, and variadic `*parts` lower to opaque
WhyML vals with NO contracts. Functions that use them cannot be body-proven.
Mark each affected function `#@ \abstract` with `assigns \nothing` and NO
`ensures` — this emits a bodyless `val` (zero TCB growth) and suppresses the
body's type error. The Python body is RETAINED for runtime. NEVER use
`\trusted`.

### Pure-Python string-op reimplementation bypasses rfind/split/variadic opacity

When a string-op body is blocked by `rfind`/`split`/`*parts` opacity, REWRITE
with `len` + indexing + slicing + concat (all body-verifiable: `str_length_op` /
`str_sub_op` / `str_concat_op`) before resorting to `\abstract`. Replace
`path.rfind('/')` with a `while i >= 0` tail scan using `path[i] == '/'`. Keep
`return`/`break` OUT of loops (they emit unbound `Return` exceptions). Accept
only SMT-tractable postconditions (length bounds); route `\forall`-position
properties to Rocq/Lean.

### Tuple / heterogeneous-seq return type defaults to int

A function returning `(s1, s2)` (string tuple) or `[(top, dirs, nondirs)]` (list
of heterogeneous tuples) emits a type error: the tuple/seq component-type
inference defaults to `int` regardless of the body's component types. Workaround:
narrow the return to an INT (e.g. a bounded count) — body-verifiable, preserves a
totality consequence. For a function that MUST return structured data, keep it
`\abstract` (zero-TCB) and log the GAP.

### Class import does not materialize module-global object instances

When a formal-test driver needs a CLASS from a module that defines module-global
object instances (e.g. `_filesystem`), do NOT import the class — it emits
`val constant _filesystem : int` (not the record type), causing ill-typed stubs.
Instead, import FUNCTION wrappers that construct the object internally. Function
imports materialize the World global correctly.

---

## Anti-patterns

- **Using `\trusted`** — defeats the purpose. If PyCSL can't prove
  something, identify the missing feature precisely and document it.
- **Abstraction over concrete implementations** — pycsl_lib modules are
  real runnable Python, not stubs. Test them concretely first.
- **Ignoring formal test failures** — a formal test failure means the
  postcondition is wrong or the implementation has a bug. Fix it.
- **Fighting the tool** — if body-level proof is blocked by 5+ tool
  gaps, switch to stub-level formal tests. Document the gaps and
  move on. Consider the thin API wrapper pattern for partial coverage.
- **Forgetting `PYTHONHASHSEED=0`** — results become non-deterministic
  without it. Always set it.
- **Forgetting `: str` return types where appropriate** — PyCSL maps
  `str` to Why3 `string` correctly. Use `-> str` when the real Python
  function returns a string.  String equality and `\length(\result)`
  work in postconditions.  Only string *method calls* are unsupported.
- **Putting functions in a submodule and re-exporting** — function
  contracts don't propagate through `__init__.py` re-exports. Put
  annotated functions directly in `__init__.py` (classes are fine in
  submodules).
- **Running from the wrong CWD** — PyCSL resolves imports from CWD.
  Run from the repo root so `src/pycsl_lib/` and `src/pycsl_lib_test/` resolve.

---

## Related files

- `docs/glossary/formal-test.md` — defines the formal test concept
- `docs/glossary/axiom-registry.md` — defines the axiom registry concept
- `src/pycsl/module6_whyml/preamble.py` — `_AXIOM_REGISTRY` source of truth
- `test-suite/corpus/pycsl-reference/0342.py` — GCD flagship proof (axiom pattern)
- `lib/calling.json` — call graph of stdlib symbols to cover
