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

---

## CENSUS TAKEN (2026-09-09) — **ZERO live sites in this tree**

An AST census over `src/self-annotate/src`, `src/pycsl` and both corpora, counting `if <x>:` /
`if not <x>:` truthiness guards where `<x>` is a dict/set-typed PARAMETER, a local bound to a
dict/set literal or `dict()`/`set()`, or a dict/set-declared `self.<field>`, inside a
`@mutable_state` class:

    src/self-annotate/src   0        src/pycsl   0        both corpora   0

**So route #55 is a live unsoundness of the LANGUAGE with no current instance in this tree**,
and that is a real finding rather than an anticlimax — it is the opposite of routes #46/#50/#51,
each of which turned out to be live in the mirror. Two consequences, and they pull in
opposite directions:

  * a repair is very likely **byte-inert on both planes**, so its cost is near zero and none
    of the three candidates has to fight for its place on cost grounds;
  * but the repair defends FUTURE programs rather than correcting any proof that exists
    today, so it must not be sold as fixing a live defect. Route #55 is a language defect a
    user reaches with an ordinary dict parameter and an ordinary postcondition.

**Caveat, stated so the number is not over-trusted**: this is a SYNTACTIC census. The arm the
27th plane records keys on the emitter's SYMBOL TABLE, so a name the symbol table types as a
dict/set without a syntactic dict/set annotation or literal — a `getattr(self, "_x", {})`
alias, for instance — would not be counted here. The exact site count needs the emitter
instrumentation the plane used for the emit_ir twin
(`scratchpad/w49/always_present_trace.patch`), run over the 53-file mirror emission. That
measurement is OWED before any repair lands, because the census says where to look and only
the measurement is the gate.

---

## THE BLUNT REPAIR WAS BUILT, MEASURED, AND **DELIBERATELY NOT LANDED**
## (2026-09-09; patch kept at `scratchpad/w51/r55.patch`)

Candidate (3) — replace the constant with a PER-NAME opaque bool (route #41's device;
spelled `val function pycsl_nonempty_<name> : bool`, a nullary val rather than a predicate
over the map because the map's WhyML type varies by site and Why3 has no polymorphic abstract
val to key on it) — was built and it WORKS: all three false proofs (`f2`, `c2`, `c3`) fail
closed under it, and the three controls stay closed.

**Then the emission diff was read, and it changed the conclusion.** This is the same method
that found route #50: *measure a fix and read the diff it produces.*

    mirror emission: 1 of 53 moves — `module6_whyml/expressions.py`, THREE lines

So the syntactic census's own caveat was right and the number ZERO was wrong: there IS one
live site, reached through the SYMBOL TABLE rather than through a syntactic dict annotation.
It is this, in the emitter's own expression lowering:

```python
    if subst and name in subst:
```

```whyml
    if (let __and_l = (if true then 1 else 0) in                       (* before *)
        if __and_l <> 0 then (if (match Map.get subst !name with Some _ -> true | None -> false end) ...
    if (let __and_l = (if pycsl_nonempty_subst then 1 else 0) in ...   (* after  *)
```

**And at THAT site the constant is HARMLESS.** `true and (name in subst)` is equivalent to
`name in subst`, which is exactly what Python computes — if `subst` is empty then
`name in subst` is False anyway, so the short-circuit changes nothing. The justification
recorded in the 27th plane ("the `in` does the real check") is **correct about the shape it
describes**; what is wrong is that the arm ALSO fires OUTSIDE that shape, on the bare guard,
which is what `c2` demonstrated.

**Landing the blunt opaque would therefore**: fix nothing that is live, LOSE PRECISION at the
one live site (an opaque left conjunct can be false where `name in subst` is true, so the
guard weakens), and owe a whole-file re-proof of `module6_whyml/expressions.py` — one of the
two slowest mirrors in the tree. That is a bad trade and it is recorded as a REFUSED repair,
not as an oversight.

## RECOMMENDED REPAIR (for the next stretch): MAKE THE ARM MATCH ITS OWN JUSTIFICATION

Keep the constant `true` exactly where the justification holds — the guard is the LEFT
CONJUNCT of an `and` whose remaining conjunct is a membership test on the SAME name, so the
following check subsumes it — and answer the per-name OPAQUE on the bare guard. Then:

  * the one live mirror site keeps its current emission **byte-identical**, so no re-proof is
    owed at all, and
  * `f2`/`c2`/`c3` fail closed, because none of them has a subsuming `in`.

This needs the PARENT context at the `_to_bool` call (the `and` lowering, not the leaf), which
is why it is a real build rather than a one-line change; it is the honest shape of the fix and
its blast radius is measured in advance at ZERO.

---

# STATUS — CLOSED (2026-09-09). The repair is the SHAPE, not the type.

The recommended repair above was built and landed. `true` is answered only where this
truthiness test is the **LEFT CONJUNCT of an `and` whose other conjunct is a membership test
on the SAME name** — there an empty map makes that test False anyway, so `true` is EXACT
rather than an over-approximation — and every other dict/set present-guard gets a per-name
opaque `bool` (route #41's device, spelled as a nullary `val function` because the map's
WhyML type varies by site and Why3 has no polymorphic abstract val to key on it).

The mark is made at the `and` lowering, where the PARENT is visible, and consumed at the leaf
in `_to_bool`; that is why it is a real build rather than a one-line change, and it is what
makes the repair byte-inert.

## MEASURED AT THE LANDED TREE

  * mirror emission — **0 of 53 move**; the one live site (`module6_whyml/expressions.py`,
    `if subst and name in subst:`) is byte-identical, so **NO re-proof is owed**
  * corpus byte-diff — **0 of 905** pre-existing emissions move
  * both fidelity planes byte-identical to HEAD's own runs
  * L3-tc inherited 53/53 (the emission is byte-identical to a set already measured 53/53)
  * metric UNCHANGED — markers 456 / grep 481 / offset 25 / unattached 0
  * `mirror-coverage` rc=0 at 550/41; raises-honesty rc=0 at 70; doc-coherency rc=0;
    doc §T.5.12s
  * witnesses `1104` (dict) / `1105` (set) / `1106` (list control) FAIL CLOSED, and `1107`
    (the subsumption precision guard) PROVES — negative-tested BOTH ways: it proves with the
    exemption and FAILS without it

## THE 27th PLANE FOUND THIS AND THEN CAUGHT ITS OWN STALENESS

`bin/check-type-keyed-constant-answers.py` is where the route came from — its baseline named
the risk and said nothing checked it. When the lowering changed, the SAME plane refused to go
green: it reported the new `[_r55_subsumed_name]` arm as unclassified AND the old
`[_current_self_type+_current_symbol_table+_mutable_state_classes]` entry as matching no arm
("the lowering changed and the classification is stale"). Both are now written, and the
plane records **0 OPEN** for the first time this campaign — route #51's entry moved from OPEN
to CLOSED in the same increment.
