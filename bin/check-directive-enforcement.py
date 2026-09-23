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
MIN_COVERED = 32


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
        "'    d.disk[0] = v\n'",
        '# pycsl-flags: --memory-model hoare\n\n#@ happy inode_conf(n):\n#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]\n\n#@ class invariant \\length(self.disk) >= 1024\nclass Disk:\n    def __init__(self) -> None:\n        self.disk: list = [0] * 1024\n\n\nd = Disk()\n\n\n#@ requires 0 <= k and k < 8\n#@ footprint inode_conf(k)\n#@ assigns d.disk\ndef writer(k: int, v: int) -> None:\n'
        "'    d.disk[512 + k * 64] = v\n'",
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
    for name in sorted(CASES):
        viol, sat, flags = CASES[name]
        v_got, v_out = verdict(viol, flags)
        s_got, s_out = verdict(sat, flags)
        if v_got == "SUCCESS":
            bad.append((name, "the VIOLATING program VERIFIES — the directive is not enforced",
                        v_out))
        elif s_got != "SUCCESS":
            bad.append((name, "the SATISFYING program does not verify (%s) — the directive "
                        "may be enforced by rejecting the construct outright" % s_got, s_out))
        elif args.verbose:
            print("    ok       %-28s violate=%-8s satisfy=SUCCESS" % (name, v_got))

    for name in sorted(ASSUMPTION_CASES):
        without, with_, flags = ASSUMPTION_CASES[name]
        w_got, w_out = verdict(without, flags)
        d_got, d_out = verdict(with_, flags)
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
