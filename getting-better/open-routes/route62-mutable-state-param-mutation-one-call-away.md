# OPEN ROUTE #62 — THE `@mutable_state` COLLECTION-PARAM NO-OP IS GUARDED ONLY IN THE
# MUTATING FUNCTION'S OWN CONTRACT, SO THE MUTATION ESCAPES ONE CALL AWAY
# (found 2026-09-11 by relaunch #55, at `a79e7e8b`)

## THE HEADLINE

```python
@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def helper(self, s: Set[int]) -> None:
        s.add(1)                       # <- mutation lives HERE, contract names nothing

    #@ requires 1 not in s
    #@ ensures 1 not in s              # <- FALSE of the program
    #@ assigns \nothing
    def caller(self, s: Set[int]) -> None:
        self.helper(s)
```

**`[+] Verification SUCCESS! All contracts formally proven.`** CPython: after `caller(s)`,
`1 not in s` is **False**. The emission carries the same tell as routes #60 and #61 —
`warning: unused variable s`.

BOTH DIRECTIONS MEASURED: the FALSE `ensures 1 not in s` PROVES; the TRUE twin
`ensures 1 in s` does NOT prove. Unsound in the SILENT direction.

## THE DECORATOR IS WHAT OPENS IT — MEASURED, NOT INFERRED

The IDENTICAL program with `@mutable_state` removed is **REFUSED**:

> in-place mutation of dict/set parameter 's' (`s.add(...)`) is out of scope: Python mutates
> a dict/set argument BY REFERENCE, so the write must be visible to the caller …

So `@mutable_state` converts a HARD REFUSAL into a SILENT NO-OP. That much is already
documented in `docs/pycsl-static-semantics-reference.md`, which says in as many words that
the exemption rests on *"a claim about the corpus, not a property of the lowering"* and that
*"the exemption now holds only while its own justification does."*

## WHAT IS NEW HERE IS THAT THE CONTAINMENT GUARD IS KEYED TOO NARROWLY

A guard already exists for the DIRECT case and it fires correctly — put the same contract on
the same function as the mutation and you get:

> `s.add(...)` mutates the collection PARAMETER `s`, **which this function's own contract also
> NAMES** … Measured: `#@ requires 1 not in s` / `#@ ensures 1 not in s` over a body
> `s.add(1)` proved SUCCESS.

**"THIS FUNCTION'S OWN CONTRACT" IS THE DEFECT.** Split the program across two methods —
mutation in one with a contract that names nothing, observation in the other — and the guard
never fires, while the model still lowers the mutation to a no-op. The `\nothing` frame on
`helper` is simultaneously the thing that makes the escape possible and a FALSE statement
about Python, where `s.add(1)` writes the caller's set.

**THIS IS THE FOURTH TIME THIS WINDOW A GUARD KEYED ON THE LOCAL FUNCTION HAS BEEN DEFEATED
BY MOVING ONE STEP.** Route #59's carrier 7 (the planned repair watched the local, the hazard
moved to a second field), route #60 (the fold watched store sites, the hazard moved into a
loop), route #61 (the fold watched literal keys, the hazard moved to names), and now this.
**When a guard's condition names a syntactic location, ask what the same program looks like
with that location one call, one branch, or one binding away.**

## EXTENT, MEASURED

  * SET param via `s.add(...)` inside `@mutable_state`: **BROKEN** (the headline).
  * DICT param via a SUBSCRIPT STORE `d[1] = 99`: **REFUSED**, unconditionally and
    independently of the decorator — that store has its own hard boundary.
  * Same set program WITHOUT `@mutable_state`: **REFUSED**.
  * Not yet measured: other dict/set MUTATING METHODS one call away (`update`, `setdefault`,
    `discard`, `clear`), and a chain longer than one call.

## THE SHAPE A REPAIR HAS TO TAKE

The guard must stop keying on the mutating function's own contract. The cheapest sound
extension that preserves the exemption's purpose: **refuse when the mutating function is
called anywhere in the unit with an argument that is a collection PARAMETER of the calling
function** — at that point the no-op is observable by the caller's contract, which is exactly
the condition the current guard is trying to express, just measured at the wrong frame. A
refusal is the safe direction and matches every other repair in this family.
