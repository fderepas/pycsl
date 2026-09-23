# Route #216 (CLOSED, same night) — a DUNDER override erases the Liskov obligation, and the run says "All contracts formally proven"

**Found:** 2026-09-23, gen #30, while trying to make the undemonstrated refusal
`module6_whyml/functions.py::PYCSL-SUBTYPING-PAIR` fire.

**Family:** route #97. Same defect class — *the substitutability obligation is never
recorded, so it is never checked, and the run reports success* — with a NEW trigger. #97
was a FIELDLESS base; this is a DUNDER method name. #97 is closed; this is not.

## The decisive signature

Two files identical except for **one identifier**.

```python
class Base:
    #@ ensures \result >= 5
    def m(self) -> int:
        return 5

class Sub(Base):
    #@ ensures \result == 0
    def m(self) -> int:
        return 0
```

`--check-behavioral-subtyping` (hoare): **`[-] Verification FAILED`**. The emission carries

```
  let base__m (self: base) : int
  let sub__m  (self: sub)  : int
  goal sub__m_refines_base :
```

and the goal is unprovable, which is exactly right: `\result == 0` does not refine
`\result >= 5`.

Rename `m` to `__len__` in both classes and change nothing else:

    [+] Verification SUCCESS! All contracts formally proven.

The emitted module is, in its entirety:

```
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  type sub = {  }

end
```

No `base__...`, no `sub__...`, **no goal**. Both methods are dropped from emission, the
override pair is never recorded, and the substitutability claim the flag was asked to
check silently evaporates — while the tool prints the strongest sentence it has.

CPython ground truth: `C().__len__()` is `0` and `len(C())` is `0`, so a client that reads
`Base.__len__`'s `\result >= 5` off the declared hierarchy is wrong, and nothing told it.

## The same hole through the OTHER door: `#@ conforms_to`

Protocol conformance records its pairs in `Module5_IREmitter` rather than in
`ir_resolve.apply_inheritance`, and it has the same hole:

```python
class P(Protocol):
    #@ ensures \result >= 5
    def m(self) -> int: ...

#@ conforms_to P
class C:
    #@ ensures \result == 0
    def m(self) -> int: return 0
```

`m` -> **FAILED**, with `goal c__m_refines_p` in the emission.
`__len__` -> **SUCCESS**, with `type p = {  }` and nothing else.

So this is not one collection site's bug: it is the DROP of dunder methods from emission
reaching two independent obligation recorders.

## Why the existing refusal does not catch it

`PYCSL-SUBTYPING-PAIR` (module6_whyml/functions.py) exists precisely to stop this:

> "...but the base method `...` is not among the emitted functions, so the Liskov
> refinement goal cannot be built. Emitting nothing here would report the file as fully
> proven with the substitutability obligation silently absent (route #97), so this is a
> refusal."

It fires when a pair was **recorded** and cannot be **resolved**. Here the pair is never
recorded at all, because the dunder never becomes an emitted function that a collector can
see. **The guard covers "recorded but unresolvable" and not "never recorded", and the
second is the reachable one.** That is also why the refusal is one of the sites
`check-refusal-witness-coverage` lists as undemonstrated.

## Blast radius (measured)

* 49 non-`__init__` dunder defs in the corpus, 10 in the mirror, 14 in the live tree, 8 in
  `src/pycsl_lib` (the census witness 1800 already carries).
* This route needs a dunder OVERRIDE (a base/protocol member and a subclass member of the
  same dunder name) plus `--check-behavioral-subtyping`. **MEASURED: ZERO such pairs
  exist** — 1722 corpus files, 53 mirror, 94 live, 104 `pycsl_lib`, all scanned by AST for
  a class whose base (by name, same file) defines the same non-`__init__` dunder. So the
  route is LATENT: nothing in the repository exercises it today, and no repair would move
  a byte of the current emission.

  That cuts both ways and the second way is the reason it is written down. A hole nothing
  in the corpus touches is a hole no gate will ever report, and this one produces the
  strongest sentence the tool can print over a module with no content in it. It is exactly
  the shape a USER hits first, because `__len__`, `__eq__` and `__lt__` are the methods a
  Python class overrides.

## Carriers

* `getting-better/open-routes/route216-carrier-inheritance-dunder.py` — expects SUCCESS
  (the false certificate). Its TRUE twin, the same file with `m` instead of `__len__`,
  FAILS.
* `getting-better/open-routes/route216-carrier-protocol-dunder.py` — expects SUCCESS.

Both are registered in `bin/check-open-route-carriers.py`, so the day either one stops
reporting SUCCESS the plane says so.

## CLOSED by option 1, the same night

Three candidate shapes were considered, in increasing cost:

1. **REFUSE the combination** — chosen. If `--check-behavioral-subtyping` is on and a
   class overrides (or conforms to) a DUNDER that will not be emitted, refuse rather than
   certify.
2. **Record the pair anyway and let `PYCSL-SUBTYPING-PAIR` do its job.** The refusal's
   message is already exactly right for this case; it simply never sees the pair. REJECTED
   for now: it means editing `ir_resolve` and `Module5_IREmitter`, both UN-TRUSTED mirror
   twins, which owes a verbatim mirror edit and a whole-file re-proof.
3. **Emit dunders.** The real fix, and the same one witness 1800 is waiting on. Large: an
   explicitly-called dunder currently lowers to a contractless `val`, and making it a `let`
   changes emission broadly — byte-diff-RISKY, so authorize-first. Still open as work.

`PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED` is raised in `pycsl.py::_run_pipeline`, **whose
mirror twin is `\trusted`** — the choke-point rule — so the refusal costs no marker, no
mirror edit and no re-proof. Mirror sync re-measured after landing: 887 verbatim, unmoved.

It cannot retire an earlier refusal (lesson (n3)): it fires only on DUNDER pairs, and a
dunder pair is precisely what no other check can see.

### The four things that were checked, not assumed

| program | flag | before | after |
|---|---|---|---|
| dunder override, contracts conflict (1805) | on | **SUCCESS** | REFUSED |
| `#@ conforms_to` dunder member (1806) | on | **SUCCESS** | REFUSED |
| dunder, NO override (1807) | on | PASS | PASS |
| the same violation spelled `m` (1808) | on | FAIL | FAIL |

Plus two negative controls run by hand: two UNRELATED classes each defining `__len__`
under the flag still verify (the guard is on the PAIR, not on dunders), and a dunder
override with the flag OFF still verifies (no default run changes at all).

### Still owed, and named

The refusal makes the tool stop LYING about this pair. It does not make the pair checkable
— that is option 3, and witness 1800 is the standing reminder. A user who wants
substitutability checked on `__len__` must today rename the method, which the refusal's
message says in as many words.
