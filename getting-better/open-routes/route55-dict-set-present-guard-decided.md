# OPEN ROUTE #55 — `if <dict/set param>:` IS DECIDED TRUE, AND A REAL POSTCONDITION IS THEN
# PROVED OVER A STRICT SUBSET
# (found 2026-09-09 by relaunch #50, immediately after closing route #51)

**Found by following the 27th plane's OWN NAMED FOLLOW-UP.** `bin/check-type-keyed-constant-
answers.py` classifies sixteen type-keyed arms that answer a Why3 bool constant. Fifteen are
justified; the justification for the dict/set present-guard arm is a claim about the
CONTRACTS rather than about the lowering — *"sound for the type-safety+frame contracts the
mirror carries, because deleting a branch cannot make an `ensures True` false"* — and the
baseline says in as many words that **nothing checks that claim**. This is what happens when
you write a real postcondition instead of `ensures True`.

## THE DEMONSTRATION (`scratchpad/w51/frame/f2.py`, `[+] Verification SUCCESS` at `a46fa6b7`)

```python
@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures \result == 7        # <-- FALSE: `o.probe({})` returns 0 in Python
    #@ assigns \nothing
    def probe(self, d: Dict[int, int]) -> int:
        if d:
            if 1 in d:
                return 7
            return 7
        return 0

o = C(); assert o.probe({}) == 0      # runs, and holds
```

The emitted body shows the whole defect on one line:

```whyml
  let c__probe (self: c) (d: map int (option int)) : int
    ensures  { (result = 7) }
  =
    if true then begin raise (Return 7) end else begin raise (Return 0) end
```

`if d:` is the literal **`true`**, so the `else` arm — the one Python takes for an EMPTY dict
— is unreachable, and `ensures \result == 7` is proved over a STRICT SUBSET of the reachable
states. This is routes #50/#51's sentence at a different type and a different connective:
*the model decided from a TYPE where only a value fact could justify it.* A dict/set is
modelled as a `map` with no int value, so the `<> 0` truthiness coercion would be a TYPE
ERROR; `true` was chosen as the over-approximation that lets the following `in` happen.

## FOUR CONTROLS, ALL MEASURED AT `a46fa6b7`, AND TWO OF THEM SHARPEN THE PLANE'S OWN TEXT

| probe | shape | verdict |
|---|---|---|
| `f2.py` | `Dict` param, present-guard **then** a membership test | **PROVES a false contract** |
| `c2.py` | `Dict` param, **NO membership test at all** | **PROVES a false contract** |
| `c3.py` | `Set` param | **PROVES a false contract** |
| `c4.py` | `List` param | fails closed (a list carries a length model) |
| `c1.py` | `f2` without `@mutable_state` | fails closed — the gate is exact |
| `f1.py` | the FRAME half: `self.tag = 7` on the deleted branch, `assigns \nothing` | fails closed |

**`c2` contradicts the arm's own description.** The baseline calls it *"`if <dict/set param>:`
as a PRESENT-guard before a membership test"* and justifies `true` as *"the over-approximation
that lets the real check — the `in` that follows — happen"*. There need be no `in` that
follows: the arm fires on the bare guard, so the justification does not describe the arm that
exists.

**The FRAME half of the named follow-up does NOT reproduce** (`f1`), which is worth recording
as carefully as the half that does: the `assigns` proof is not fooled in this shape. The
`ensures` half is the live one.

## SCOPE — AND WHY IT IS NOT ONLY A MIRROR CONCERN

The plane's scope claim is about the MIRROR (all seven methods that reach these arms carry
`#@ ensures True`, measured at `42a4f84b`, and that measurement stands). But PyCSL is a
general-purpose verifier: the file above is an ordinary annotated program with an ordinary
postcondition, and it is `@mutable_state`-gated exactly as routes #50 and #51 were — which is
the same gate those two live mirror defects sat behind.

## CENSUS — NOT YET TAKEN

Owed before any repair: how many `if <dict/set>:` present-guards exist in the mirror and the
corpora, and how many sit in a method carrying a REAL postcondition (as opposed to
`ensures True`). The plane already knows the mirror answer for the emit_ir twin — nine sites
in seven methods, all `ensures True` — but the dict/set arm has not been counted.

## CANDIDATE REPAIRS (costs NOT yet measured)

1. **Refuse the guard.** `if <dict/set>:` has no faithful bool in this model, so reject it
   and make the program write `len(d) > 0` / an explicit emptiness test. Fail-closed and
   honest; blast radius unmeasured.
2. **Give the map a size.** Route #31 already carries a KNOWN-SIZE model for some
   collections; if the size is available the guard is `size > 0`, which is EXACT. This is the
   completeness-gaining direction and is the same move that made routes #45/#50/#54 gains
   rather than retreats.
3. **Opaque the guard.** An abstract `bool` keyed on the map, undecidable both ways. Cheapest,
   and consistent with the `pycsl_none_str` device, but buys no precision.
