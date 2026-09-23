# Route #216 (OPEN) — a DUNDER override erases the Liskov obligation, and the run says "All contracts formally proven"

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
  same dunder name) plus `--check-behavioral-subtyping`. Corpus occurrences of that
  combination: to be counted before any repair is priced.

## Carriers

* `getting-better/open-routes/route216-carrier-inheritance-dunder.py` — expects SUCCESS
  (the false certificate). Its TRUE twin, the same file with `m` instead of `__len__`,
  FAILS.
* `getting-better/open-routes/route216-carrier-protocol-dunder.py` — expects SUCCESS.

Both are registered in `bin/check-open-route-carriers.py`, so the day either one stops
reporting SUCCESS the plane says so.

## Repair sketch (NOT landed, deliberately)

Three candidate shapes, in increasing cost:

1. **REFUSE the combination.** If `--check-behavioral-subtyping` is on and a class
   declares an override (or a conformance) of a method that will not be emitted, refuse
   rather than certify. Cheap, fail-closed, and consistent with the choke-point rule — but
   it must be placed where it cannot retire an earlier refusal (lesson (n3)).
2. **Record the pair anyway and let `PYCSL-SUBTYPING-PAIR` do its job.** The refusal's
   message is already exactly right for this case; it simply never sees the pair.
3. **Emit dunders.** The real fix, and the same one witness 1800 is waiting on. Large:
   an explicitly-called dunder currently lowers to a contractless `val`, and making it a
   `let` changes emission broadly — byte-diff-RISKY, so authorize-first.

The choice is NOT made here, because pricing it needs the corpus count above and a
byte-diff, and this window did not do either.
