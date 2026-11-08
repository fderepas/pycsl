# OPEN ROUTE #63 — "NO ALIASING IS POSSIBLE" IS TRUE FOR LISTS AND FALSE FOR SETS
# (found 2026-09-11 by relaunch #55, at `8bea5e27`)

## THE HEADLINE — A SELF-CONTAINED FALSE PROOF, NO EXTERNAL CALLER NEEDED

```python
@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires 1 not in t
    #@ ensures \result == 0
    #@ assigns \nothing
    def helper(self, s: Set[int], t: Set[int]) -> int:
        s.add(1)
        if 1 in t:
            return 7
        return 0

    #@ requires True
    #@ ensures \result == 0          # <- FALSE: CPython returns 7
    #@ assigns \nothing
    def caller2(self) -> int:
        u: Set[int] = set()
        return self.helper(u, u)
```

**`[+] Verification SUCCESS! All contracts formally proven.`** CPython: `caller2()` returns
**7**. The true twin (`ensures \result == 7`) does NOT prove. Emission tell, for the fourth
route running: `warning: unused variable s`.

`caller2` takes no parameters and returns a concrete int. There is no "if a caller aliases"
caveat to argue about — the aliasing happens INSIDE the proven unit, and the model answers 0
for a function that returns 7.

## WHAT IT REFUTES

`test-suite/annotations.md` §5 (Hoare model) states:

> "Arrays are independent value-typed entities. `arr[i] <- v` mutates only `arr`.
> **No aliasing is possible.** `\separated` is trivially true."

and the translational reference justifies the `\separated` → literal `true` lowering with a
real MECHANISM:

> "Why3's region typing rejects an aliased array application outright ('This application
> creates an illegal alias'), so two array parameters there really are always separated."

**THAT MECHANISM IS REAL, AND IT ONLY COVERS `array`.** Measured, both sides:

  * LISTS — `f(xs, xs)` on two `List[int]` params is **REFUSED**, with Why3's own message
    `This application creates an illegal alias`. The claim holds, by the cited mechanism.
  * SETS — `self.helper(u, u)` on two `Set[int]` params **PROVES**. A set lowers to a PURE
    `map`, and a pure value **HAS NO REGION**, so there is nothing for Why3's alias
    discipline to reject. The barrier that makes the claim true for lists cannot exist here.

This is the same asymmetry route #59 turned on, arriving at a second consequence: **a list is
region-typed so Why3 polices it; a dict/set is a pure map so nothing does.** The phrase "no
aliasing is possible" is a statement about `array` that has been generalised to collections.

## IT IS A COMPOUND, AND BOTH HALVES ARE NEEDED — MEASURED

  * WITHOUT `@mutable_state` the identical program is **REFUSED** ("in-place mutation of
    dict/set parameter `s`"), so the `@mutable_state` no-op exemption is what supplies the
    mutation vehicle.
  * The DICT analogue via a subscript store (`s[1] = 5`) is **REFUSED** independently — that
    store has its own hard boundary. The live vehicle is the set mutator `.add`.

## RELATION TO ROUTE #62, CLOSED HOURS EARLIER

Route #62's guard refuses a contract-named dict/set formal passed to a call, and it DOES fire
on the parameter-passing spelling of this exploit (`caller(self, u)` calling
`self.helper(u, u)` — refused, measured). **It does not fire here, because `u` is a LOCAL,
not a formal, and the caller's contract names only `\result`.** So this is the same "guard
keyed on a location" pattern for the FIFTH time in one generation: #59's carrier 7, #60's
loop, #61's names, #62's call boundary, and now a LOCAL instead of a parameter.

## THE REPAIR SHAPE

Narrow and in the safe direction: **in a `@mutable_state` class, refuse a call that passes
the SAME dict/set-typed name in two or more argument positions.** That is exactly the shape
whose post-state the by-value model cannot represent, it needs no callee resolution, and it
leaves every single-occurrence call — which is what the mirror's reflecting handlers do —
untouched. A longer-term fix is to make `\separated` and the "no aliasing" claim conditional
on the ARRAY model rather than stated for all collections.
