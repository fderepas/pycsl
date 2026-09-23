#!/usr/bin/env python3
r"""check-directive-enforcement.py — DOES EACH `#@` DIRECTIVE ACTUALLY BITE?

WHY THIS EXISTS (#49, gen #31). The campaign has a plane for whether every directive is
DOCUMENTED on all five normative surfaces (`bin/doc-coherency.py`), a plane for whether every
refusal has a WITNESS proving it can fire (`check-refusal-witness-coverage.py`), and a plane
for whether a refusal's ADVICE is followable (`check-refusal-advice-audited.py`). It had no
plane for the most basic question a user asks:

    >>> IF I WRITE THIS DIRECTIVE AND THEN VIOLATE IT, DOES ANYTHING HAPPEN?

Two routes in one afternoon were exactly that question answered NO:
  * ROUTE #219 — a `#@ happy ... postcond` SECURITY policy targeting a dunder was accepted
    by Module 3 and never checked, because Module 5 dropped the method.
  * ROUTE #222 — a `#@ requires` on an `@overload` stub was read by the parser, attached to
    the AST node, and thrown away with it; a call violating it was ACCEPTED.
Neither was a REFUSAL that failed to fire, so the refusal planes could not see them; neither
was an undocumented directive, so doc-coherency could not see them. They were directives that
were read and then ignored, and the only instrument that finds those is one that WRITES THE
VIOLATION AND RUNS IT.

HOW A CASE WORKS. Each covered directive gets a PAIR:
  * VIOLATE — a program where the directive is FALSE of the code. It must NOT report
    `Verification SUCCESS`. (FAILED and REFUSED are both acceptable: a refusal is a
    perfectly good way to enforce a directive, and several here do exactly that.)
  * SATISFY — the nearest program where the directive HOLDS. It must verify.
The SATISFY half is not decoration: without it a directive "enforced" by a compiler that
rejects the construct outright would pass the VIOLATE half and mean nothing. It is the same
control discipline routes #13 and #223 already pay for.

COVERAGE IS DERIVED, NOT LISTED. The directive population comes from
`doc-coherency.extract_directives_from_annotations()` — the canonical `test-suite/annotations.md`
— so a NEW directive lands UNCOVERED and lowers the fraction. That is the ratchet: MIN_COVERED
only goes up, and the uncovered set is printed by name every run so the debt has members
rather than a number.

WHY THE UNCOVERED SET IS NOT JUST "NOT DONE YET". Nine directives have no pair, and the
reason differs by kind. FOUR of them have no pair because **there is no violating program
to write** — the directive has no enforced consequence, which is itself a result and is
filed as a finding rather than papered over with a vacuous pair:

  * `mixin`           — neither documented consequence is enforced; a class named in
                        `#@ compose_from` need not carry the marker, and a `#@ mixin` class
                        may be instantiated directly. See
                        `getting-better/open-routes/finding-mixin-marker-has-no-teeth.md`.
  * `thread_entry`    — `ConcurrencyChecker` collects the names into `_thread_entries`,
                        which is never read; the IR key has no Module-6 consumer. The
                        UB-7.3 refusal fires identically with and without it.
  * `releases`        — parsed onto `node.csl_releases`, read by nothing (and honestly
                        documented as informational). Both in
                        `finding-thread-entry-and-releases-are-inert.md`.
  * `mutex_invariant` — bites at the release point, but the emitted
                        `_check_initial_lock_counter` asserts the invariant of an
                        unconstrained `val ref`, so the SATISFYING half cannot pass in any
                        program. All 19 corpus drivers that declare it pass `--no-proof`.
                        See `finding-mutex-invariant-initial-check-unprovable.md`.

The remaining FIVE are pair-shaped but out of reach of a single-file harness:
`reveal` (a no-op within the owning unit by design — needs two units and `--import-path`),
`verify_module` and `proof` (need a second module / real Rocq-Lean artifacts),
`sibling_concrete` (probed: Why3's own type invariants hold at a `val` boundary, so the
documented advantage is not observable in a minimal program), and `propagate_frame`
(probed and CONFIRMED to propagate — with the marker the stub gains
`ensures { forall i [decode (self.d[i])]. … }`, without it only `writes { self.d }` — but
the frame's trigger term must be a `Call` (`_frame_trigger_term`), and the callee it names
is emitted as a program `let`, so the minimal carrier dies on `unbound function or
predicate symbol`).

A pair whose satisfying half cannot pass is not a pair. The covered fraction here is a
floor on ENFORCED directives, not on parsed ones.

Usage:  bin/check-directive-enforcement.py [--verbose] [--list-uncovered]
Exit 1 if any covered directive fails its pair, or coverage falls below the ratchet.
Exit 2 if the population cannot be derived (a refusal, never a pass).
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = os.path.join(ROOT, ".venv", "bin", "python3")
PY = PY if os.path.exists(PY) else "python3"
DRIVER = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

# (#49) gen #31 — the floor. It starts at the number of pairs written in the commit that
# introduced the plane, and only ever rises. A directive whose pair is DELETED, or a new
# directive added to annotations.md without one, drops the fraction and turns this red.
MIN_COVERED = 44


def population():
    """The canonical directive set, DERIVED from annotations.md via doc-coherency."""
    spec = importlib.util.spec_from_file_location(
        "_dc", os.path.join(ROOT, "bin", "doc-coherency.py"))
    mod = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["doc-coherency.py"]
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass
    finally:
        sys.argv = argv
    return set(mod.extract_directives_from_annotations())


_ANCHOR = "_ = 0  # anchor\n"

# The shared preamble for the CONCURRENT family: one protected global, two locks,
# and a `#@ thread_entry` worker. Each case supplies only the worker's BODY.
_CONC_HDR = (
    "# pycsl-flags: --memory-model concurrent --strict-concurrent-checks --no-proof\n#@ shared counter protected_by lock_counter\n#@ mutex_invariant lock_counter: counter >= 0\nimport threading\nlock_counter = threading.Lock()\nlock_other = threading.Lock()\ncounter = 0\n_ = 0  # anchor\n\n\n#@ thread_entry\n#@ \\diverges\n#@ requires True\n#@ ensures True\ndef worker() -> int:\n")


# The `#@ lock_order` header: TWO protected globals and a declared total order, with the
# order itself left as a `%s` slot. The worker body is fixed; only the order varies.
_LOCK_ORDER_HDR = (
    "# pycsl-flags: --memory-model concurrent --strict-concurrent-checks --no-proof\n"
    "#@ shared counter protected_by lock_counter\n"
    "#@ shared other protected_by lock_other\n"
    "#@ lock_order %s\n"
    "#@ mutex_invariant lock_counter: counter >= 0\n"
    "import threading\nlock_counter = threading.Lock()\nlock_other = threading.Lock()\n"
    "counter = 0\nother = 0\n_ = 0  # anchor\n\n\n"
    "#@ thread_entry\n#@ \\diverges\n#@ requires True\n#@ ensures True\n"
    "def worker() -> int:\n"
    "    #@ critical lock_counter\n    with lock_counter:\n        counter = 1\n"
    "        #@ critical lock_other\n        with lock_other:\n            other = 1\n"
    "    return 0\n")


# --- the MIXIN family (annotations.md §2.7, corpus 0549-0553) -------------------------
# Three skeletons, because the family's directives bite in three different places: the
# COMPOSITION algebra (provides / compose_from / requires_method), the field
# CLASSIFICATION (shared_state / touches_field) and the dependency CONTRACT
# (depends_method). Each skeleton leaves exactly one slot open so the pair differs by the
# directive under test and nothing else.
#
# NOT COVERED, AND MEASURED, NOT ASSUMED: `#@ mixin` itself. Its two documented
# consequences are "marks the class as a composable mixin" and "not instantiated
# directly", and NEITHER is enforced — a class named in `#@ compose_from` is flattened
# whether or not it carries the marker (measured: the flagship 0549 with `#@ mixin`
# deleted from `CoreEmit` still verifies), and a `#@ mixin` class instantiated directly
# verifies too (both halves SUCCESS). There is no violating program to write, so `mixin`
# stays in the UNCOVERED list rather than getting a pair that would pass vacuously. It is
# not a soundness hole — the flatten-and-re-verify compensation (S2b, finding w66) still
# checks the real provider — it is a directive with no teeth, which is the other thing
# this plane exists to name.
_MIX_ALGEBRA = (
    "# pycsl-flags: --memory-model hoare\n_ = 0  # anchor\n\n%s\n"
    "#@ mixin\nclass MapOps:\n"
    "    #@ %s emit: (self, x: int) -> int\n"
    "    #@   ensures \\result >= 0\n"
    "    #@ provides handle_get\n"
    "    #@ ensures \\result >= 0\n    #@ assigns \\nothing\n"
    "    def handle_get(self, k: int) -> int:\n        return self.emit(k)\n\n\n"
    "#@ compose_from %s\nclass Facade:\n"
    "    #@ ensures \\result >= 0\n    #@ assigns \\nothing\n"
    "    def run(self, k: int) -> int:\n        return self.handle_get(k)\n")
_MIX_PROVIDER = (
    "\n#@ mixin\nclass CoreEmit:\n"
    "    #@ shared_state program_ir: int\n%s"
    "    #@ ensures \\result >= 0\n    #@ assigns \\nothing\n"
    "    def emit(self, x: int) -> int:\n        return x if x >= 0 else 0\n\n")
# The field-classification skeleton: the `%s` slot is the declaration of `cache`.
_MIX_FIELD = (
    "# pycsl-flags: --memory-model hoare\n_ = 0  # anchor\n\n\n"
    "#@ mixin\nclass CoreEmit:\n%s"
    "    #@ provides emit\n"
    "    #@ ensures \\result >= 0\n    #@ assigns self.cache\n"
    "    def emit(self, x: int) -> int:\n        self.cache = x\n"
    "        return x if x >= 0 else 0\n\n\n"
    "#@ compose_from CoreEmit\nclass Facade:\n"
    "    def __init__(self) -> None:\n        self.cache: int = 0\n\n"
    "    #@ ensures \\result >= 0\n    #@ assigns self.cache\n"
    "    def run(self, k: int) -> int:\n        return self.emit(k)\n")
# The dependency-contract skeleton: `%s` is the bound BOTH the declared dependency and
# every downstream `ensures` claim. The provider always returns 0.
_MIX_DEP = (
    "# pycsl-flags: --memory-model hoare\n_ = 0  # anchor\n\n\n"
    "#@ mixin\nclass CoreEmit:\n    #@ provides emit\n"
    "    #@ ensures \\result >= 0\n    #@ assigns \\nothing\n"
    "    def emit(self, x: int) -> int:\n        return 0\n\n\n"
    "#@ mixin\nclass MapOps:\n"
    "    #@ depends_method emit: (self, x: int) -> int\n"
    "    #@   ensures \\result >= %s\n"
    "    #@ provides handle_get\n"
    "    #@ ensures \\result >= %s\n    #@ assigns \\nothing\n"
    "    def handle_get(self, k: int) -> int:\n        return self.emit(k)\n\n\n"
    "#@ compose_from CoreEmit, MapOps\nclass Facade:\n"
    "    #@ ensures \\result >= %s\n    #@ assigns \\nothing\n"
    "    def run(self, k: int) -> int:\n        return self.handle_get(k)\n")


# directive -> (violating source, satisfying source, extra flags)
# Each violating source must NOT verify; each satisfying source must verify.
CASES = {
    "requires": (
        _ANCHOR + '\n\n#@ requires x > 100\n#@ ensures \\result == x\n'
        'def f(x: int) -> int:\n    return x\n\n\n'
        '#@ ensures \\result == 0\ndef use() -> int:\n    return f(0)\n',
        _ANCHOR + '\n\n#@ requires x > 100\n#@ ensures \\result == x\n'
        'def f(x: int) -> int:\n    return x\n\n\n'
        '#@ ensures \\result == 101\ndef use() -> int:\n    return f(101)\n', []),
    "ensures": (
        _ANCHOR + '\n\n#@ ensures \\result == 5\ndef f() -> int:\n    return 1\n',
        _ANCHOR + '\n\n#@ ensures \\result == 5\ndef f() -> int:\n    return 5\n', []),
    "assigns": (
        _ANCHOR + '\n\nclass C:\n    def __init__(self) -> None:\n        self.v: int = 0\n\n'
        '    #@ assigns \\nothing\n    def go(self) -> int:\n        self.v = 7\n        return 0\n',
        _ANCHOR + '\n\nclass C:\n    def __init__(self) -> None:\n        self.v: int = 0\n\n'
        '    #@ assigns self.v\n    def go(self) -> int:\n        self.v = 7\n        return 0\n', []),
    "class": (   # `#@ class invariant`
        _ANCHOR + '\n\n#@ class invariant self.v >= 0\nclass C:\n'
        '    def __init__(self) -> None:\n        self.v: int = 0\n\n'
        '    #@ assigns self.v\n    def go(self) -> int:\n        self.v = -1\n        return 0\n',
        _ANCHOR + '\n\n#@ class invariant self.v >= 0\nclass C:\n'
        '    def __init__(self) -> None:\n        self.v: int = 0\n\n'
        '    #@ assigns self.v\n    def go(self) -> int:\n        self.v = 1\n        return 0\n', []),
    "loop": (    # `#@ loop invariant`
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ ensures \\result == 0\n'
        'def f(n: int) -> int:\n    i: int = 0\n'
        '    #@ loop invariant i == 5\n    #@ loop variant n - i\n'
        '    while i < n:\n        i = i + 1\n    return 0\n',
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ ensures \\result == 0\n'
        'def f(n: int) -> int:\n    i: int = 0\n'
        '    #@ loop invariant i >= 0\n    #@ loop variant n - i\n'
        '    while i < n:\n        i = i + 1\n    return 0\n', []),
    "no_exception": (
        _ANCHOR + '\n\n#@ no_exception \\all\ndef f() -> int:\n    d: int = 0\n    return 10 // d\n',
        _ANCHOR + '\n\n#@ no_exception \\all\ndef f() -> int:\n    d: int = 2\n    return 10 // d\n', []),
    "assert": (  # `#@ assert` (a ghost assertion in the body)
        _ANCHOR + '\n\n#@ ensures \\result == 1\ndef f() -> int:\n    x: int = 1\n'
        '    #@ assert x == 2\n    return x\n',
        _ANCHOR + '\n\n#@ ensures \\result == 1\ndef f() -> int:\n    x: int = 1\n'
        '    #@ assert x == 1\n    return x\n', []),
    "\\variant": (  # `#@ \variant` — the function variant (termination)
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ \\variant 0\n#@ ensures \\result == 0\n'
        'def f(n: int) -> int:\n    if n > 0:\n        return f(n - 1)\n    return 0\n',
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ \\variant n\n#@ ensures \\result == 0\n'
        'def f(n: int) -> int:\n    if n > 0:\n        return f(n - 1)\n    return 0\n', []),
    "allow_iteration_mutation": (
        # WITHOUT the acknowledgement, UB-7.1 refuses; that is the directive's whole job,
        # so the VIOLATE half here is the ABSENCE of it. The list is a LOCAL, not a
        # parameter: an in-place `append` to a list PARAMETER is refused for an unrelated
        # reason (the caller-visible frame), which would have made the SATISFY half fail for
        # something this case is not about — measured on the first run of this plane, and a
        # good illustration of why the satisfying twin is not decoration.
        _ANCHOR + '\nfrom typing import List\n\n\n#@ ensures \\result >= 0\n'
        'def go() -> int:\n    xs: List[int] = [1, 2, 3]\n    n: int = 0\n    for x in xs:\n'
        '        xs.append(x)\n        n = n + 1\n    return n\n',
        _ANCHOR + '\nfrom typing import List\n\n\n#@ ensures \\result >= 0\n'
        'def go() -> int:\n    xs: List[int] = [1, 2, 3]\n    n: int = 0\n'
        '    #@ allow_iteration_mutation\n    for x in xs:\n'
        '        xs.append(x)\n        n = n + 1\n    return n\n',
        # `--no-proof`, for the reason the project's OWN witness gives. Corpus 0407 — the
        # only file that exercises this directive — carries `# pycsl-flags: --no-proof` and
        # says why: "a full proof would need loop invariants". A loop over a list the body
        # GROWS has no termination measure, and measured here it times out at 51M steps.
        # The UB-7.1 detector is a PIPELINE refusal that runs before any proof, so the
        # VIOLATE half is unaffected by the flag; what the SATISFY half then shows is that
        # the acknowledgement lets the construct THROUGH the detector, which is precisely
        # what the directive is for. Stated rather than hidden: this pair's satisfying side
        # is weaker than the others', and it is weaker in the same way 0407 already is.
        ["--no-proof"]),
    "happy": (
        '# pycsl-flags: --memory-model hoare\n'
        '#@ happy no_decrease:\n#@     targets bump\n'
        '#@     postcond self.v >= \\old(self.v)\n'
        'class C:\n    def __init__(self) -> None:\n        self.v: int = 5\n\n'
        '    #@ assigns self.v\n    def bump(self) -> int:\n        self.v = 0\n        return 0\n',
        '# pycsl-flags: --memory-model hoare\n'
        '#@ happy no_decrease:\n#@     targets bump\n'
        '#@     postcond self.v >= \\old(self.v)\n'
        'class C:\n    def __init__(self) -> None:\n        self.v: int = 5\n\n'
        '    #@ assigns self.v\n    def bump(self) -> int:\n'
        '        self.v = self.v + 1\n        return 0\n',
        ["--memory-model", "hoare"]),
    # (#49) ROUTE #224 — THIS CASE RUNS WITH `--check-behavioral-subtyping` ON PURPOSE,
    # and the reason is a finding this plane made on its FIRST RUN. By DEFAULT the violating
    # program VERIFIES: `#@ conforms_to P` populates the `overrides` list, and ONLY
    # `--check-behavioral-subtyping` emits the refinement goal, so a declared conformance
    # whose contract does NOT refine the protocol's reports `All contracts formally proven`
    # with no warning of any kind. annotations.md §12.15's own opening sentence says the
    # directive "declar[es] that a class conforms to the named protocols, SYNTHESIZING
    # per-method contract-refinement VCs", which is what a reader takes away; the mechanism
    # paragraph three lines later gates the goal on the flag.
    # The case is run WITH the flag so this plane measures what it is for — does the
    # directive BITE when its checking is on — and the DEFAULT gap is held separately as
    # route #224's carrier, the same division of labour routes #212/#213/#214 already use.
    "conforms_to": (
        _ANCHOR + '\nfrom typing import Protocol\n\n\nclass P(Protocol):\n'
        '    #@ ensures \\result == 99\n    def m(self) -> int: ...\n\n\n'
        '#@ conforms_to P\nclass C:\n    def __init__(self) -> None:\n        self.v: int = 0\n\n'
        '    #@ ensures \\result == 1\n    def m(self) -> int:\n        return 1\n',
        _ANCHOR + '\nfrom typing import Protocol\n\n\nclass P(Protocol):\n'
        '    #@ ensures \\result == 99\n    def m(self) -> int: ...\n\n\n'
        '#@ conforms_to P\nclass C:\n    def __init__(self) -> None:\n        self.v: int = 0\n\n'
        '    #@ ensures \\result == 99\n    def m(self) -> int:\n        return 99\n',
        ["--check-behavioral-subtyping", "--memory-model", "hoare"]),
    "check": (   # `#@ check <expr>` — prove here, do NOT assume downstream
        _ANCHOR + '\n\n#@ ensures \\result == 1\ndef f() -> int:\n    x: int = 1\n'
        '    #@ check x == 2\n    return x\n',
        _ANCHOR + '\n\n#@ ensures \\result == 1\ndef f() -> int:\n    x: int = 1\n'
        '    #@ check x == 1\n    return x\n', []),
    "raises": (  # `#@ raises E when <cond>` — an exceptional postcondition
        # VIOLATE: the body raises when the condition is FALSE (`n >= 0` raises although the
        # clause says it only raises when `n < 0`).
        _ANCHOR + '\n\n#@ raises ValueError when n < 0\n#@ ensures \\result == 0\n'
        'def f(n: int) -> int:\n    raise ValueError("always")\n',
        _ANCHOR + '\n\n#@ raises ValueError when n < 0\n#@ ensures \\result == 0\n'
        'def f(n: int) -> int:\n    if n < 0:\n        raise ValueError("neg")\n'
        '    return 0\n', []),
    "assumes": (  # `#@ assumes bounded_int(N)` — machine integers, overflow VCs
        # WIDTH 32 IN BOTH HALVES, and the reason is this plane's own first finding: the
        # pair was originally written with `bounded_int(8)`, and BOTH halves failed —
        # because why3's `mach.int` has no `Int8` at all, so the emission ended on a library
        # error rather than on anything to do with the directive. That is now a PyCSL
        # refusal (`PYCSL-SEM-BOUNDED-INT-WIDTH`, witnesses 1840/1841), and this pair tests
        # what it is supposed to: the OVERFLOW VC the directive generates. The violating
        # half adds to an unbounded `x` so the sum can exceed 2^31-1; the satisfying half
        # bounds it.
        _ANCHOR + '\n\n#@ assumes bounded_int(32)\n#@ requires x >= 0\n'
        '#@ ensures \\result >= 0\ndef f(x: int) -> int:\n    return x + 20\n',
        _ANCHOR + '\n\n#@ assumes bounded_int(32)\n#@ requires 0 <= x and x <= 100\n'
        '#@ ensures \\result >= 0\ndef f(x: int) -> int:\n    return x + 20\n', []),
    "ghost": (   # `#@ ghost <name> = <expr>` — a model-only variable, usable in invariants
        # VIOLATE: the ghost counter is maintained correctly but the invariant asserts a
        # relation that is FALSE of it, so the loop invariant fails.
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ ensures \\result == n\n'
        'def f(n: int) -> int:\n    i: int = 0\n    #@ ghost count = 0\n'
        '    #@ loop invariant 0 <= i and i <= n\n    #@ loop invariant count == i + 1\n'
        '    #@ loop variant n - i\n    while i < n:\n        #@ ghost count += 1\n'
        '        i = i + 1\n    return i\n',
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ ensures \\result == n\n'
        'def f(n: int) -> int:\n    i: int = 0\n    #@ ghost count = 0\n'
        '    #@ loop invariant 0 <= i and i <= n\n    #@ loop invariant count == i\n'
        '    #@ loop variant n - i\n    while i < n:\n        #@ ghost count += 1\n'
        '        i = i + 1\n    return i\n', []),
    "\\diverges": (  # `#@ \diverges` — no termination proof required
        # VIOLATE: a loop with NO variant and NO `\diverges` must not verify (termination
        # is an obligation). SATISFY: the same loop WITH the acknowledgement.
        _ANCHOR + '\n\n#@ requires n >= 0\n#@ ensures \\result >= 0\n'
        'def f(n: int) -> int:\n    i: int = 0\n'
        '    #@ loop invariant i >= 0\n    while i < n:\n        i = i + 1\n    return i\n',
        _ANCHOR + '\n\n#@ \\diverges\n#@ requires n >= 0\n#@ ensures \\result >= 0\n'
        'def f(n: int) -> int:\n    i: int = 0\n'
        '    #@ loop invariant i >= 0\n    while i < n:\n        i = i + 1\n    return i\n', []),
    # THE CONCURRENT FAMILY. `--no-proof` for the reason the corpus's OWN concurrency
    # witnesses give (0417 and 0259 both carry it): these checks are STATIC concurrency
    # analysis that runs before any proof, and the proof side of a `#@ \diverges` thread
    # entry is not what the directives are about. Each violating half is a REFUSAL, which
    # is exactly how this family is enforced.
    "shared": (   # `#@ shared X protected_by L` — X may only be touched holding L
        _CONC_HDR + '    counter = 1\n    return 0\n',
        _CONC_HDR + '    #@ critical lock_counter\n    with lock_counter:\n'
        '        counter = 1\n    return 0\n',
        ["--memory-model", "concurrent", "--strict-concurrent-checks", "--no-proof"]),
    "critical": (  # `#@ critical L` — this `with` block is a critical section for L
        # VIOLATE: the block is annotated (and takes) the WRONG lock for `counter`.
        _CONC_HDR + '    #@ critical lock_other\n    with lock_other:\n'
        '        counter = 1\n    return 0\n',
        _CONC_HDR + '    #@ critical lock_counter\n    with lock_counter:\n'
        '        counter = 1\n    return 0\n',
        ["--memory-model", "concurrent", "--strict-concurrent-checks", "--no-proof"]),
    "acquires": (  # `#@ acquires L` — the explicit-acquire spelling of `#@ critical`
        # VIOLATE: the block names (and takes) the WRONG lock for `counter`, so UB-7.3 fires.
        # The documented claim is that `acquires` and `critical` are EQUIVALENT in Module5/6;
        # this pair is what makes that claim falsifiable rather than a sentence in a table.
        _CONC_HDR + '    #@ acquires lock_other\n    with lock_other:\n'
        '        counter = 1\n    return 0\n',
        _CONC_HDR + '    #@ acquires lock_counter\n    with lock_counter:\n'
        '        counter = 1\n    return 0\n',
        ["--memory-model", "concurrent", "--strict-concurrent-checks", "--no-proof"]),
    "lock_order": (  # `#@ lock_order m1, m2` — a TOTAL order on nested acquisition
        # Needs its own header (a second protected global, and the order declaration itself),
        # so it does not reuse _CONC_HDR. The body is IDENTICAL in both halves — it takes
        # lock_counter and then, still holding it, lock_other. Only the DECLARED order moves.
        # That is the point: the directive is the entire difference between the two runs, so
        # a `lock_order` that were parsed and filed away would make both halves verify.
        _LOCK_ORDER_HDR % "lock_other, lock_counter",
        _LOCK_ORDER_HDR % "lock_counter, lock_other",
        ["--memory-model", "concurrent", "--strict-concurrent-checks", "--no-proof"]),
    "provides": (  # `#@ provides <m>` — THIS method is the provider a sibling depends on
        # VIOLATE: delete the marker and `emit` is still there, still verified, still
        # callable — but no longer OFFERED, so `MapOps`'s dependency has no provider and
        # composition is refused by name.
        _MIX_ALGEBRA % (_MIX_PROVIDER % "", "depends_method", "CoreEmit, MapOps"),
        _MIX_ALGEBRA % (_MIX_PROVIDER % "    #@ provides emit\n", "depends_method",
                        "CoreEmit, MapOps"),
        ["--memory-model", "hoare"]),
    "compose_from": (  # `#@ compose_from M1, M2` — the composition itself
        # VIOLATE: name only `CoreEmit`. `MapOps` is then never flattened, so `Facade.run`
        # calls a `handle_get` the composer does not have. The provider mixin is present
        # and correct in BOTH halves — only the composition list moves.
        _MIX_ALGEBRA % (_MIX_PROVIDER % "    #@ provides emit\n", "depends_method",
                        "CoreEmit"),
        _MIX_ALGEBRA % (_MIX_PROVIDER % "    #@ provides emit\n", "depends_method",
                        "CoreEmit, MapOps"),
        ["--memory-model", "hoare"]),
    "requires_method": (  # `#@ requires_method` — an ABSTRACT operation the composer supplies
        # VIOLATE: compose `MapOps` alone. The abstract `emit` it was verified against has
        # no provider in the composition, so the hole is never filled — refused.
        _MIX_ALGEBRA % ("", "requires_method", "MapOps"),
        _MIX_ALGEBRA % (_MIX_PROVIDER % "    #@ provides emit\n", "requires_method",
                        "CoreEmit, MapOps"),
        ["--memory-model", "hoare"]),
    "shared_state": (  # `#@ shared_state <f>: <t>` — DELIBERATELY shared facade state (D1)
        # VIOLATE: write `self.cache` with no classification at all (corpus 0551's shape).
        # SATISFY: classify it as shared. The `touches_field` case below is the SAME
        # violating program with the other classification — which is the honest way to say
        # that what is enforced is "classify the field", and the two spellings then differ
        # in the ownership rule (one owner vs many), not in whether the write is allowed.
        _MIX_FIELD % "",
        _MIX_FIELD % "    #@ shared_state cache: int\n",
        ["--memory-model", "hoare"]),
    "touches_field": (  # `#@ touches_field <f>: <t>` — an OWNED field (at most one owner)
        _MIX_FIELD % "",
        _MIX_FIELD % "    #@ touches_field cache: int\n",
        ["--memory-model", "hoare"]),
    "depends_method": (  # `#@ depends_method <m>: <sig>` + its declared contract
        # VIOLATE: declare that `emit` returns >= 1 and draw the consequence through
        # `handle_get` up to `Facade.run`. The provider returns 0. The composed file FAILS.
        # Worth knowing exactly WHERE it fails, because the obligation named S2b
        # (`provider refines dependency`) has NO implementation — `ir_resolve` says so in
        # a comment: it is discharged by the FLATTENING, which re-emits `handle_get`
        # against the concrete `CoreEmit.emit` and cannot prove >= 1. Verified by reading
        # the emitted WhyML for this exact file: `mapops__handle_get` proves against the
        # ASSUMED `val self_emit_1 ensures { result >= 1 }`, and it is `facade__handle_get`
        # — the clone — that fails. This pair is therefore a regression test on the
        # COMPENSATION, not on a check: anything that made flattening lazier would turn it
        # green while re-opening route #95's severity-1 shape.
        _MIX_DEP % ("1", "1", "1"),
        _MIX_DEP % ("0", "0", "0"),
        ["--memory-model", "hoare"]),
    "for": (  # `#@ for k in range(lo, hi):` — BOUNDED macro-expansion, one ground clause per index
        # Both halves have the SAME body and the same `ensures`; only the range's upper bound
        # moves, 3 vs 4. With `range(0, 3)` the fourth byte carries no bound, so the sum's
        # `<= 1020` is unprovable. That is the precise thing the directive promises and the
        # precise thing a wrong implementation would get wrong in either direction: an
        # expansion that ignored the range (or quietly emitted a `\forall k` over the whole
        # index space instead of ground clauses) would make BOTH halves verify.
        _ANCHOR + '\n\n#@ requires \\length(buf) >= 4\n#@ for k in range(0, 3):\n'
        '#@     requires 0 <= buf[k] and buf[k] <= 255\n'
        '#@ ensures \\result >= 0 and \\result <= 1020\n'
        'def sum4(buf: list) -> int:\n    return buf[0] + buf[1] + buf[2] + buf[3]\n',
        _ANCHOR + '\n\n#@ requires \\length(buf) >= 4\n#@ for k in range(0, 4):\n'
        '#@     requires 0 <= buf[k] and buf[k] <= 255\n'
        '#@ ensures \\result >= 0 and \\result <= 1020\n'
        'def sum4(buf: list) -> int:\n    return buf[0] + buf[1] + buf[2] + buf[3]\n', []),
    "no_inline": (  # `#@ no_inline` — verify the body ONCE, reuse the CONTRACT at callers
        # VIOLATE: the body does not satisfy its own `ensures`, which must still be checked —
        # the whole soundness argument for `no_inline` is that the callee stays a verified
        # `let` (a false `ensures` fails AT the callee, nothing moves into the TCB). If this
        # verified, the directive would be a `\trusted` in disguise.
        _ANCHOR + '\n\n#@ no_inline\n#@ ensures \\result == 7\n#@ assigns \\nothing\n'
        'def seven() -> int:\n    return 1\n\n\n'
        '#@ ensures \\result == 7\ndef caller() -> int:\n    return seven()\n',
        _ANCHOR + '\n\n#@ no_inline\n#@ ensures \\result == 7\n#@ assigns \\nothing\n'
        'def seven() -> int:\n    return 7\n\n\n'
        '#@ ensures \\result == 7\ndef caller() -> int:\n    return seven()\n', []),
    "interface": (  # `#@ interface ensures ...` — the narrow contract importers see
        # VIOLATE: an interface clause the DEFINITION does not imply. The narrowing VC
        # (definition => interface) is emitted in the owning `let` and must fail.
        _ANCHOR + '\n\n#@ ensures \\result == 7\n#@ interface ensures \\result == 9\n'
        'def f() -> int:\n    return 7\n',
        _ANCHOR + '\n\n#@ ensures \\result == 7\n#@ interface ensures \\result >= 1\n'
        'def f() -> int:\n    return 7\n', []),
    "label": (   # `#@ label L` + `\at(e, L)` — the value of `e` at the label point
        # VIOLATE: the postcondition relates the post-write element to its value at the
        # label with the WRONG offset (+3 where the body adds 2). If `\at` were lowered to
        # the CURRENT value rather than the value AT the label, `arr[0] == \at(arr[0], PRE)`
        # would be trivially true and a wrong offset would be the only thing that could
        # fail — so the satisfying twin uses the RIGHT offset and must prove.
        '# pycsl-flags: --memory-model typed\n' + _ANCHOR +
        '#@ requires \\length(arr) >= 1\n'
        '#@ ensures arr[0] == \\at(arr[0], PRE) + 3\n#@ ensures \\result == k\n'
        'def bump_at(arr: list, k: int) -> int:\n    #@ label PRE\n'
        '    arr[0] = arr[0] + 2\n    return k\n',
        '# pycsl-flags: --memory-model typed\n' + _ANCHOR +
        '#@ requires \\length(arr) >= 1\n'
        '#@ ensures arr[0] == \\at(arr[0], PRE) + 2\n#@ ensures \\result == k\n'
        'def bump_at(arr: list, k: int) -> int:\n    #@ label PRE\n'
        '    arr[0] = arr[0] + 2\n    return k\n',
        ["--memory-model", "typed"]),
    "fresh_globals": (
        # An ASSUMPTION-SHAPED directive that nonetheless fits the VIOLATE/SATISFY frame,
        # because what it assumes is a CONSTRUCTOR POST-STATE rather than a contract: a
        # module-global is havoc'd at every entry, so WITHOUT the directive the assertion
        # about its freshly-constructed value cannot be proved, and WITH it, it can. The
        # "violation" here is the absence, exactly as for `allow_finalizer`.
        _ANCHOR + '\n\nclass Counter:\n    #@ assigns self.n\n'
        '    #@ ensures self.n == 0\n    def __init__(self) -> None:\n'
        '        self.n: int = 0\n\n\ncounter = Counter()\n\n\n'
        '#@ requires True\n#@ ensures \\result == 0\n'
        'def probe() -> int:\n    #@ assert counter.n == 0\n'
        '    return counter.n\n',
        _ANCHOR + '\n\nclass Counter:\n    #@ assigns self.n\n'
        '    #@ ensures self.n == 0\n    def __init__(self) -> None:\n'
        '        self.n: int = 0\n\n\ncounter = Counter()\n\n\n'
        '#@ requires True\n#@ ensures \\result == 0\n'
        '#@ fresh_globals\ndef probe() -> int:\n'
        '    #@ assert counter.n == 0\n    return counter.n\n', []),
    "footprint": (  # `#@ footprint H(arg)` — every write must stay inside H's region
        # NO `except` CLAUSE, and that is a finding of its own kind: the corpus example
        # (0614) exempts a `formatter` it also DEFINES, and `happy`'s exempt-set check
        # rejects a name that is not a method in the module — "a typo in the exempt set
        # would silently widen the property's coverage, so this is rejected". Copying the
        # header WITHOUT that function refuses BOTH halves, which is what the satisfying
        # twin is for: it caught a case where the whole pair was measuring the exempt-set
        # check rather than the footprint containment it is named after.
        # VIOLATE: the body writes `d.disk[0]`, which is OUTSIDE inode `k`'s region
        # `[512 + k*64, 512 + (k+1)*64)` for every legal `k`. The meta-pass injects a
        # CONTAINMENT `#@ check` at each write, and it must not discharge.
        '# pycsl-flags: --memory-model hoare\n\n#@ happy inode_conf(n):\n#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]\n\n#@ class invariant \\length(self.disk) >= 1024\nclass Disk:\n    def __init__(self) -> None:\n        self.disk: list = [0] * 1024\n\n\nd = Disk()\n\n\n#@ requires 0 <= k and k < 8\n#@ footprint inode_conf(k)\n#@ assigns d.disk\ndef writer(k: int, v: int) -> None:\n'
        '    d.disk[0] = v\n',
        '# pycsl-flags: --memory-model hoare\n\n#@ happy inode_conf(n):\n#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]\n\n#@ class invariant \\length(self.disk) >= 1024\nclass Disk:\n    def __init__(self) -> None:\n        self.disk: list = [0] * 1024\n\n\nd = Disk()\n\n\n#@ requires 0 <= k and k < 8\n#@ footprint inode_conf(k)\n#@ assigns d.disk\ndef writer(k: int, v: int) -> None:\n'
        '    d.disk[512 + k * 64] = v\n',
        ["--memory-model", "hoare"]),
    "uses": (   # `#@ uses L` — cite lemma L so its general fact is in scope
        # An ASSUMPTION-SHAPED pair like `fresh_globals`: the goal `\forall x: Nat.
        # to_int(x) >= 0` needs INDUCTION and is not SMT-dischargeable directly. WITHOUT
        # the citation the lemma is not in scope and the goal fails; WITH it the lemma is
        # emitted first and the fact discharges. The pair therefore also covers `#@ lemma`
        # in the only way that means anything — a lemma nobody cites proves nothing for
        # anybody.
        _ANCHOR + '\n\n#@ datatype Nat = Z | S(Nat)\n\n\n#@ \\variant n\n#@ assigns \\nothing\ndef to_int(n: Nat) -> int:\n    match n:\n        case Z():\n            return 0\n        case S(m):\n            return 1 + to_int(m)\n\n\n#@ lemma\n#@ ensures to_int(n) >= 0\n#@ \\variant n\n#@ assigns \\nothing\ndef to_int_nonneg(n: Nat) -> None:\n    match n:\n        case Z():\n            pass\n        case S(m):\n            to_int_nonneg(m)\n\n\n#@ ensures \\forall x: Nat; to_int(x) >= 0\n''#@ assigns \\nothing\ndef all_nonneg() -> int:\n    return 0\n',
        _ANCHOR + '\n\n#@ datatype Nat = Z | S(Nat)\n\n\n#@ \\variant n\n#@ assigns \\nothing\ndef to_int(n: Nat) -> int:\n    match n:\n        case Z():\n            return 0\n        case S(m):\n            return 1 + to_int(m)\n\n\n#@ lemma\n#@ ensures to_int(n) >= 0\n#@ \\variant n\n#@ assigns \\nothing\ndef to_int_nonneg(n: Nat) -> None:\n    match n:\n        case Z():\n            pass\n        case S(m):\n            to_int_nonneg(m)\n\n\n#@ ensures \\forall x: Nat; to_int(x) >= 0\n''#@ uses to_int_nonneg\n#@ assigns \\nothing\n'
        'def all_nonneg() -> int:\n    return 0\n', []),
    # THE `act` FAMILY, all four from one corpus shape (0455's guarded-case clamp). Each
    # pair changes exactly the clause it is named after and leaves the rest alone, so a
    # failure attributes to the directive under test rather than to the program.
    "act": (     # an act's `ensures` must hold on its guarded branch
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result == 10\n#@ act big:\n#@     given x >= 10\n'
        '#@     ensures \\result == 10\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n',
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result == x\n#@ act big:\n#@     given x >= 10\n'
        '#@     ensures \\result == 10\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n', []),
    "given": (   # the GUARD selects which branch the act's ensures is checked against
        # Same `ensures \result == x` in both halves; only the GUARD moves. Under
        # `given x >= 10` the body returns 10, so the clause is false exactly where the
        # guard now points.
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x >= 10\n'
        '#@     ensures \\result == x\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n',
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result == x\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n', []),
    "complete": (  # the guards must COVER the precondition's domain
        # Both halves use a domain-true `ensures` so ONLY the coverage claim can fail.
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result >= 0\n#@ complete small\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n',
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result >= 0\n#@ act big:\n#@     given x >= 10\n'
        '#@     ensures \\result >= 0\n#@ complete small, big\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n', []),
    "disjoint": (  # the guards must not OVERLAP
        # `given x >= 5` overlaps `given x < 10` on 5..9. Both halves use a domain-true
        # `ensures` so ONLY the disjointness claim can fail.
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result >= 0\n#@ act big:\n#@     given x >= 5\n'
        '#@     ensures \\result >= 0\n#@ disjoint small, big\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n',
        _ANCHOR + '\n\n#@ requires x >= 0\n#@ act small:\n#@     given x < 10\n'
        '#@     ensures \\result >= 0\n#@ act big:\n#@     given x >= 10\n'
        '#@     ensures \\result >= 0\n#@ disjoint small, big\n' + 'def clamp10(x: int) -> int:\n    if x < 10:\n        return x\n    return 10\n', []),
    "datatype": (  # `#@ datatype T = A | B(T)` — an algebraic type with real semantics
        # VIOLATE: a claim FALSE of the declared constructors (`to_int(S(Z()))` is 1, not 2).
        # If the datatype were modelled opaquely the claim would be unprovable EITHER way, so
        # the satisfying twin is what shows the constructors carry meaning.
        _ANCHOR + '\n\n#@ datatype Nat = Z | S(Nat)\n\n\n#@ \\variant n\n#@ assigns \\nothing\ndef to_int(n: Nat) -> int:\n    match n:\n        case Z():\n            return 0\n        case S(m):\n            return 1 + to_int(m)\n\n\n''#@ ensures \\result == 2\n#@ assigns \\nothing\n'
        'def one() -> int:\n    return to_int(S(Z()))\n',
        _ANCHOR + '\n\n#@ datatype Nat = Z | S(Nat)\n\n\n#@ \\variant n\n#@ assigns \\nothing\ndef to_int(n: Nat) -> int:\n    match n:\n        case Z():\n            return 0\n        case S(m):\n            return 1 + to_int(m)\n\n\n''#@ ensures \\result == 1\n#@ assigns \\nothing\n'
        'def one() -> int:\n    return to_int(S(Z()))\n', []),
    "lemma": (  # `#@ lemma` — proved HERE (not assumed, not cited): Why3 checks the body
        # VIOLATE: a lemma whose `ensures` is FALSE of its own precondition (a = b = 0 gives
        # 0, not >= 1). A `#@ lemma` that were merely REGISTERED rather than checked would let
        # this through and then export it as a usable fact — the worst failure shape available
        # to this directive, since every later goal would inherit the falsehood.
        _ANCHOR + '\n\n#@ lemma\n#@ requires a >= 0 and b >= 0\n#@ ensures a + b >= 1\n'
        '#@ assigns \\nothing\ndef sum_bound(a: int, b: int) -> None:\n    pass\n',
        _ANCHOR + '\n\n#@ lemma\n#@ requires a >= 0 and b >= 0\n#@ ensures a + b >= 0\n'
        '#@ assigns \\nothing\ndef sum_bound(a: int, b: int) -> None:\n    pass\n', []),
    "inductive": (  # `#@ inductive p(x): <rules>` — a least fixpoint, not an opaque predicate
        # VIOLATE: `even(3)` is NOT derivable from the two rules. SATISFY: `even(4)` is
        # (even(0) -> even(2) -> even(4)). The pair is what separates a REAL least fixpoint
        # from an uninterpreted predicate symbol: an opaque `even` would leave BOTH halves
        # unprovable, so the satisfying half is the half that proves the rules were emitted.
        _ANCHOR + '\n\n#@ inductive even(n: int):\n#@     even_zero: even(0)\n'
        '#@     even_step: \\forall m: int; even(m) ==> even(m + 2)\n\n\n'
        '#@ ensures even(3)\n#@ assigns \\nothing\ndef go() -> int:\n    return 0\n',
        _ANCHOR + '\n\n#@ inductive even(n: int):\n#@     even_zero: even(0)\n'
        '#@     even_step: \\forall m: int; even(m) ==> even(m + 2)\n\n\n'
        '#@ ensures even(4)\n#@ assigns \\nothing\ndef go() -> int:\n    return 0\n', []),
    "allow_finalizer": (
        # WITHOUT the acknowledgement a `__del__` is refused (UB-7.5); with it, and with an
        # honest frame, the class verifies. Route #219's build made the BODY real too.
        '""  # pycsl\n#@ class invariant self._n >= 0\nclass W:\n'
        '    def __init__(self) -> None:\n        self._n: int = 0\n\n'
        '    #@ assigns self._n\n    def __del__(self) -> None:\n        self._n = -1\n',
        '""  # pycsl\n#@ class invariant self._n >= 0\n#@ allow_finalizer\nclass W:\n'
        '    def __init__(self) -> None:\n        self._n: int = 0\n\n'
        '    #@ assigns self._n\n    def __del__(self) -> None:\n        self._n = 0\n', []),
}


# (#49) gen #31 — THE SECOND SHAPE: ASSUMPTION DIRECTIVES, where "violate it" is not a
# meaningful test because the directive's WHOLE PURPOSE is to make the compiler stop
# checking something. `#@ \trusted` says "assume this body's contract"; a body contradicting
# its contract under `\trusted` VERIFYING is the directive WORKING, not a defect, and the
# pair above would call it broken.
#
# So these get an INVERTED pair, which still has two sides and still proves the directive
# DOES SOMETHING: the program WITHOUT the directive must NOT verify, and the SAME program
# WITH it must verify. A directive that is silently ignored fails the second half; a
# directive that is a no-op fails the first. Keeping the two shapes in separate tables
# rather than flagging rows inside one is deliberate — the question each answers is
# different, and a reader should not have to check a boolean to know which one a row is.
ASSUMPTION_CASES = {
    "\\preserves": (  # `#@ \preserves` — opts a bodyless `\trusted` into the HAPPY boundary
        # An ASSUMPTION case because the directive's absence is a HARD ERROR, not a failed
        # goal: a non-exempt `\trusted` method whose `assigns` names a HAPPY-protected field
        # has no checkable body, so the region policy cannot hold unless the method PROMISES
        # preservation. Corpus 0461/0462 are this pair at full size; this is the two-method
        # miniature, and it is here so the promise keeps having teeth rather than becoming a
        # comment. WITHOUT: refused. WITH: the synthesized region-preservation `ensures` is
        # attached at the boundary and the file verifies.
        '_ = 0  # anchor\n#@ class invariant \\length(self.disk) >= 4096\n'
        '#@ happy region_integrity:\n#@     region 512 .. 2560\n'
        '#@     writes self.disk outside region\nclass Store:\n'
        '    def __init__(self) -> None:\n        self.disk: list = bytearray(4096)\n\n'
        '    #@ \\trusted reviewer: demo\n    #@ assigns self.disk\n'
        '    def ext_scrub(self, x: int) -> None:\n        self.disk[3000] = x\n',
        '_ = 0  # anchor\n#@ class invariant \\length(self.disk) >= 4096\n'
        '#@ happy region_integrity:\n#@     region 512 .. 2560\n'
        '#@     writes self.disk outside region\nclass Store:\n'
        '    def __init__(self) -> None:\n        self.disk: list = bytearray(4096)\n\n'
        '    #@ \\trusted reviewer: demo\n    #@ \\preserves\n    #@ assigns self.disk\n'
        '    def ext_scrub(self, x: int) -> None:\n        self.disk[3000] = x\n', []),
    "\\trusted": (
        _ANCHOR + '\n\n#@ ensures \\result == 99\ndef f() -> int:\n    return 1\n',
        _ANCHOR + '\n\n#@ \\trusted\n#@ ensures \\result == 99\n'
        'def f() -> int:\n    return 1\n', []),
    "\\abstract": (
        _ANCHOR + '\n\n#@ ensures \\result == 99\ndef f() -> int:\n    return 1\n',
        _ANCHOR + '\n\n#@ \\abstract\n#@ ensures \\result == 99\n'
        'def f() -> int:\n    return 1\n', []),
}


def verdict(src, flags):
    fd, path = tempfile.mkstemp(suffix=".py", prefix="direnf_", dir="/tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(src)
        p = subprocess.run([PY, DRIVER] + list(flags) + [path],
                           capture_output=True, text=True, timeout=900)
        out = (p.stdout or "") + (p.stderr or "")
        if "PIPELINE ERROR" in out:
            return "REFUSED", out
        if "Verification SUCCESS" in out:
            return "SUCCESS", out
        return "FAILED", out
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# (#49) gen #31 — RUN THE PAIRS CONCURRENTLY. This plane lives in the FAST set of
# `bin/run-soundness-planes.sh` on the explicit argument that a plane which only runs with
# `--slow` would not have protected the increments that needed it most (it found route #224
# on its first run). That argument is only honest if the plane STAYS fast, and it did not:
# at 24 prover invocations it cost ~2 minutes, at 88 it cost ~22, which is how a fast set
# quietly becomes a slow one. The pairs are INDEPENDENT — separate temp files, separate
# `pycsl.py` processes, no shared state — so the fix is a thread pool around the same
# `subprocess.run` calls, not a smaller table. Threads (not processes) because every worker
# spends its whole life blocked in `subprocess.run`, where the GIL is released.
#
# WORKERS: the machine's core count, capped at 8. Each `pycsl.py` run itself spawns provers,
# so going wider than the cores buys nothing and starts making pairs TIME OUT rather than
# fail — which would turn a green plane red for a reason that has nothing to do with any
# directive. `PYCSL_DIRENF_JOBS` overrides it for a machine that wants a different trade.
def _jobs() -> int:
    try:
        n = int(os.environ.get("PYCSL_DIRENF_JOBS", "") or 0)
    except ValueError:
        n = 0
    if n > 0:
        return n
    return max(1, min(8, (os.cpu_count() or 2)))


def run_pairs(table):
    """{name: (src_a, src_b, flags)} -> {name: (verdict_a, out_a, verdict_b, out_b)}.

    Order-independent by construction: results are keyed by name and the caller iterates
    `sorted(table)`, so the report reads identically however the pool schedules the work."""
    from concurrent.futures import ThreadPoolExecutor
    jobs = []
    for name in sorted(table):
        a, b, flags = table[name]
        jobs.append((name, 0, a, flags))
        jobs.append((name, 1, b, flags))
    out = {name: [None, None, None, None] for name in table}
    with ThreadPoolExecutor(max_workers=_jobs()) as pool:
        futs = {pool.submit(verdict, src, flags): (name, half)
                for (name, half, src, flags) in jobs}
        for fut, (name, half) in futs.items():
            got, text = fut.result()
            out[name][half * 2] = got
            out[name][half * 2 + 1] = text
    return {k: tuple(v) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--list-uncovered", action="store_true")
    args = ap.parse_args()

    try:
        pop = population()
    except Exception as exc:
        print("[!] directive-enforcement: REFUSING — cannot derive the directive population "
              "from annotations.md via doc-coherency (%s). A coverage fraction with no "
              "denominator is not a measurement. THIS IS A REFUSAL, NOT A PASS." % exc,
              file=sys.stderr)
        return 2
    if len(pop) < 40:
        print("[!] directive-enforcement: REFUSING — the derived population is %d "
              "directive(s), which is far below the documented surface. The extractor is "
              "broken. THIS IS A REFUSAL, NOT A PASS." % len(pop), file=sys.stderr)
        return 2

    unknown = sorted((set(CASES) | set(ASSUMPTION_CASES)) - pop)
    both = sorted(set(CASES) & set(ASSUMPTION_CASES))
    if both:
        print("[!] directive-enforcement: REFUSING — %d directive(s) appear in BOTH tables: "
              "%s. A directive is either enforced or assumed; being counted twice inflates "
              "coverage." % (len(both), ", ".join(both)), file=sys.stderr)
        return 2
    if unknown:
        print("[!] directive-enforcement: REFUSING — %d case(s) name a directive that is NOT "
              "in annotations.md: %s. A case that matches no directive is testing something "
              "this project does not document." % (len(unknown), ", ".join(unknown)),
              file=sys.stderr)
        return 2

    bad = []
    case_results = run_pairs(CASES)
    assumption_results = run_pairs(ASSUMPTION_CASES)
    for name in sorted(CASES):
        v_got, v_out, s_got, s_out = case_results[name]
        if v_got == "SUCCESS":
            bad.append((name, "the VIOLATING program VERIFIES — the directive is not enforced",
                        v_out))
        elif s_got != "SUCCESS":
            bad.append((name, "the SATISFYING program does not verify (%s) — the directive "
                        "may be enforced by rejecting the construct outright" % s_got, s_out))
        elif args.verbose:
            print("    ok       %-28s violate=%-8s satisfy=SUCCESS" % (name, v_got))

    for name in sorted(ASSUMPTION_CASES):
        w_got, w_out, d_got, d_out = assumption_results[name]
        if w_got == "SUCCESS":
            bad.append((name, "the program WITHOUT the directive already verifies — the "
                        "pair proves nothing about the directive", w_out))
        elif d_got != "SUCCESS":
            bad.append((name, "the program WITH the directive does not verify (%s) — the "
                        "assumption directive is not doing what it says" % d_got, d_out))
        elif args.verbose:
            print("    ok       %-28s without=%-8s with=SUCCESS  (assumption)"
                  % (name, w_got))

    covered = len(CASES) + len(ASSUMPTION_CASES)
    uncovered = sorted(pop - set(CASES) - set(ASSUMPTION_CASES))
    if args.list_uncovered:
        for d in uncovered:
            print("    uncovered  %s" % d)

    print("[*] directive-enforcement: %d of %d documented directive(s) have an "
          "enforcement pair; %d uncovered." % (covered, len(pop), len(uncovered)))
    if bad:
        for name, why, out in bad:
            print("[-]   %-28s %s" % (name, why), file=sys.stderr)
            print("        " + "\n        ".join(out.strip().splitlines()[-2:]), file=sys.stderr)
        print("[-] directive-enforcement: %d directive(s) failed their pair." % len(bad),
              file=sys.stderr)
        return 1
    if covered < MIN_COVERED:
        print("[-] directive-enforcement: COVERAGE RATCHET BROKEN — %d < %d. A pair was "
              "deleted, or a directive lost its case. Coverage only goes up."
              % (covered, MIN_COVERED), file=sys.stderr)
        return 1
    print("[+] directive-enforcement: OK — every covered directive BITES (its violation does "
          "not verify) and is not merely banned (its satisfying twin does). Ratchet %d."
          % MIN_COVERED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
