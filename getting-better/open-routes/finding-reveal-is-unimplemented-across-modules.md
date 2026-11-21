# FINDING (#49, gen #31) — `#@ reveal` is parsed and dropped; contract opacity is ONE-WAY

**STATUS: CLOSED (2026-09-24, gen #31).** Was: confirmed live by grep and by
measurement — a MISSING FEATURE whose documentation said it was present. See CLOSURE. The fifth inert directive found
by `bin/check-directive-enforcement.py`, and the only one whose documented behaviour is
contradicted rather than merely unenforced.

## WHAT THE DOCUMENTATION PROMISES

`test-suite/annotations.md` §2.10, row 2:

> **Reveal** — `#@ reveal <fn>` — Statement (at a call site) — This caller opts into
> `<fn>`'s rich definition contract at this site (its facts are otherwise hidden behind
> the interface). **Within the owning unit it is a no-op** (the definition is the visible
> `let`); **across modules it cites the exported definition-fact.**

The first half is true by construction and corpus `0660` tests it. The second half is the
entire point of the feature — `#@ interface` hides the rich contract so importers stay
cheap, and `#@ reveal` is how the one importer that needs it pays for it — and it is not
implemented.

## THE DATA PATH, WHICH STOPS ONE STAGE SHORT

| stage | what happens |
|---|---|
| `Module2_Parser.py:1345` | `if kw == "reveal": self.advance(); return Reveal(self.expect_name())` |
| `Module3_Weaver.py:312`  | `node.csl_reveal.append(c.fn)` |
| `Module5_IREmitter.py:6332` | `"reveal": list(getattr(node, 'csl_reveal', []) or [])` |
| Module 6 / `core_ir_semantic` | **no consumer.** `grep -rn '"reveal"' src/pycsl/module6_whyml/ src/pycsl/Module6_WhyMLTranspiler.py src/pycsl/core_ir_semantic.py` returns nothing. |

## THE MEASUREMENT

Two files, `--import-path` pointing at their directory. `packlib.py`:

```python
#@ requires 0 <= a and a <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures \result[0] * 256 + \result[1] == a     # the rich DEFINITION
#@ interface ensures \length(\result) == 2        # the narrow INTERFACE
def pack16(a: int) -> list:
    return bytes([a // 256, a % 256])
```

and a caller that needs the definition's fact, in two variants differing ONLY by one line:

```python
#@ reveal pack16                 # <-- present in one half, absent in the other
#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == x
def caller(x: int) -> int:
    d = pack16(x)
    return d[0] * 256 + d[1]
```

| variant | result |
|---|---|
| WITHOUT `#@ reveal` | FAILED (expected — only the interface is visible) |
| WITH `#@ reveal`    | **FAILED — identically** |

And the emitted WhyML for the two is **byte-identical** (`diff` clean), with the import
stub carrying only the interface:

```whyml
  val pack16 (a: int) : array int
    requires { ((0 <= a) && (a <= 65535)) }
    ensures  { ((Array.length result) = 2) }        (* the definition's fact is GONE *)
```

The narrowing VC `pack16__narrows_ens_0` IS emitted and IS proved, so the *hiding* half of
Track B works. Only the *opting back in* half is missing.

## WHY IT IS NOT A ROUTE, AND WHY IT STILL MATTERS

Nothing false is provable: the importer sees strictly less than the definition establishes,
which is sound. The cost is expressiveness with a wrong label on it — a user who reads the
table and writes `#@ interface` on a heavy function, planning to `#@ reveal` at the two
call sites that need the detail, will find those call sites simply cannot be discharged,
with no diagnostic saying why. §2.10's own motivation ("the codec's 18 per-field
`ensures` … verified once but only burdens the call sites that reveal it") describes a
workflow that does not currently exist.

## CONSEQUENCE FOR THE PLANE

`reveal` stays UNCOVERED in `bin/check-directive-enforcement.py`: the satisfying half
cannot pass, so there is no pair. The plane's module docstring previously listed it as
"pair-shaped but out of reach of a single-file harness" — that is now known to be the
wrong reason, and the docstring says so.

## THE FIX, WHEN SOMEONE PRICES IT

The import-stub builder already chooses between the definition and the interface
`ensures` when it emits a `val` for an imported function. It needs to consult the
IMPORTING function's `reveal` list and, for a named callee, emit the definition's clauses
(or a second `val`/`axiom` carrying them) at that caller. Either shape is sound by the same
argument as the narrowing VC: the definition is a proved fact about the same `let`.

Measured 2026-09-23. Files: `$SCRATCH/g31/rev/{packlib,main_v,main_s}.py`.


---

## CLOSED (2026-09-24, gen #31)

`#@ reveal <fn>` now carries the DEFINITION-fact across the import. `_emit_function`'s
interface-narrowing branch consults the importing module's `reveal` lists and, when the
function being stubbed is named by one, emits the DEFINITION contract instead of the
interface.

| file | before | after |
|---|---|---|
| importer WITHOUT `#@ reveal` (`1867`) | FAILED | FAILED (correct — opacity working) |
| importer WITH `#@ reveal pack16` (`1868`) | FAILED | **SUCCESS** |

Before the repair those two emitted BYTE-IDENTICAL `.mlw`.

**THE SCOPE IS THE MODULE, AND THAT IS WIDER THAN §2.10's SENTENCE.** The `val` stub for an
imported function is emitted ONCE per importing module, so "this caller opts in AT THIS
SITE" cannot be expressed by one stub. If ANY function in the importing module reveals
`<fn>`, the stub shows the definition. That is strictly MORE information than the
interface, and sound for exactly the reason the narrowing VC is sound: the definition is a
fact the owning unit PROVED about the same `let`. The per-site form needs a second `val`
plus call-site rewriting; it is recorded here as the refinement rather than built, and
annotations.md now says "module-scoped" instead of implying per-site.

COST, checked before the work per lesson (n4): `_emit_function`'s mirror twin is
`\trusted`, so no verbatim sync and no re-proof.

CENSUS: six corpus files used `#@ interface` or `#@ reveal`; all six keep their exact
verdicts (`0660`, `1707`-`1710`, `1847`), and the new pair `1867`/`1868` uses the
`multi_file_lib/opaque_pack.py` fixture — the corpus's existing cross-module convention.

### THE BYTE-DIFF CAUGHT THE FIRST VERSION SILENTLY DELETING AN OBLIGATION

The repair as first written cleared the interface whenever the function was revealed
ANYWHERE in the unit — including in the unit that OWNS the definition. §2.10 says reveal is
a no-op there ("the definition is the visible `let`"), and the consequence of ignoring that
was not a failure but a SHRINKING PROOF: corpus `0660` declares `#@ interface` and
`#@ reveal pack16` in one file, and the emitted `.mlw` lost

    goal pack16__narrows_ens_0 :
      forall a: int, _res: array int. ((0 <= a) && (a <= 65535)) -> …

the goal that proves the interface is a sound WEAKENING of the definition. `0660` went on
reporting `Verification SUCCESS` the whole time, with one fewer obligation discharged.

Only the byte-diff plane saw it: the sweep reported `1 MOVED, 0 GONE, 0 APPEARED` and the
one MOVED file was `0660.mlw`. **A repair that keeps every file green while deleting one of
their goals is the exact shape a per-file verdict cannot see, and the exact shape this
campaign exists to catch** — the same argument that justifies running the sweep on
increments that "obviously" only touch new code.

The fix is one word of scope: the reveal consultation now lives INSIDE the
`if emit_as_val and _iface:` branch, so it can only ever change an IMPORTED stub. The
owning unit keeps its interface and keeps its narrowing VC. Re-checked: `0660` emits
`goal pack16__narrows_ens_0` again and all eight `#@ interface`/`#@ reveal` drivers hold
their expected verdicts.
