# FINDING (gen #33, 2026-09-28) — A MECHANICAL CAUSE OF THE INT-ERASURE SEAM: THE NAME-DEDUP TIEBREAK IS STRING LENGTH

**This is ladder item 1 (backlog #64 / #62), reproduced from a minimal three-line program, and the
cause is a tiebreak nobody intended as a typing rule.**

    #@ ensures True
    def both_kappas() -> int:
        si = set(); si.add(1)      # int-keyed set    -> MONO arm
        ss = set(); ss.add("a")    # string-keyed set -> POLY arm
        return 0

    emitted:  val map_update_some (m: map int (option int)) (k: int) (v: int) : map int (option int)
    L3-tc  :  This expression has type string, but is expected to have type int

**That message is gen #32's own blocker row `string vs int` (12 occurrences), and here it is with a
three-line cause.**

## THE THREE-WAY MEASUREMENT, because two of the three are the controls

| module | decl emitted | L3-tc |
|---|---|---|
| string-keyed set ALONE (`finding-seam-by-string-length-control-string-only.py`) | **POLY** `map 'k (option 'v)` | ✓ |
| int-keyed set ALONE (`finding-seam-by-string-length-control-int-only.py`) | **MONO** `map int (option int)` | ✓ |
| **BOTH in one module** (`finding-seam-by-string-length-witness.py`) | **MONO** | **✗ string vs int** |

Each arm alone is fine. Only the COMBINATION breaks, so this is not "sets of strings are
unsupported" — it is an interaction, which is why a per-feature probe could never find it.

## THE MECHANISM, and the code says the quiet part out loud

`statements.py` picks the declaration PER SITE:

    _poly = (getattr(self, "_mutable_state_classes", None) or _set_kappa == "string")
    self._add_abstract_op(("val map_update_some (m: map 'k (option 'v)) …" if _poly else
                           "val map_update_some (m: map int (option int)) …")
                          + "    ensures { result = Map.set m k (Some v) }")

and its own comment states the assumption the whole design rests on:

>>> "the name-dedup means **ONE DECL SERVES EVERY MAP WRITE IN THE MODULE**. Corpus modules keep the
>>> fixed `map int (option int)` → byte-identical."

But `_add_abstract_op` resolves a same-arity name clash like this:

    # Same arity but different declaration — keep longer
    if len(decl) > len(existing):
        self._abstract_ops[name] = decl

`_decl_arity` (correct since relaunch #30) reads both spellings as the same arity, so the clash lands
in that branch — and **the int-MONOMORPHIC spelling is LONGER**, so it wins:

    val snapshot        (a: array 'a) : seq 'a                      35 chars   \
    val snapshot        (a: array int) : seq int                    37 chars    > MONO wins
    val map_update_some (m: map 'k (option 'v)) …                   80 chars   /
    val map_update_some (m: map int (option int)) …                 86 chars

>>> **SO A PER-SITE CHOICE BETWEEN TWO VALUE MODELS IS ARBITRATED BY STRING LENGTH, AND THE
>>> INT-ERASED SPELLING IS LONGER — FOR `snapshot` BY TWO CHARACTERS. It also wins in BOTH
>>> registration orders, because a stored decl is replaced only by a LONGER one, so this is not an
>>> order-dependent flake: whenever both spellings reach one emission, the module collapses to
>>> `int`.** The author's "one decl serves the module" is true; which one it is was never decided.

Three symbols are registered in both spellings: `map_update_some`, `map_update_none`, `snapshot`.

## WHY THIS WAS MISSED, AND WHAT FOUND IT

Not by looking at the seam. It fell out of route #228's own corollary — *check the MODULUS, not just
the hash* — which sent me to audit every minted-symbol name for the invariant **a minted name must
determine its declaration**. The seam pair was the residue of that audit. #62 ranked the seam by
ERROR CLASS and #64 corrected the unit of work to "one marker's whole CHAIN"; neither asked *what
DECIDES which value model a shared symbol gets*, and the answer is `len()`.

## HONEST RECORD OF THE TWO PROBES, because the first one measured NOTHING

My first witness paired a string-keyed SET with an int-keyed DICT and **I predicted it would fail. It
did not** — both emitted POLY, and so did its control, identically. A dict subscript store never
reaches the `_poly` site at all (`_poly` is computed inside the `set.add` arm), so the two decls never
clashed. **The control not discriminating is what exposed my wrong model; that probe is VACUOUS, not
fail-closed,** and it is logged that way. The correct construction needs two SETS with different
element kappas.

## THE REPAIR — PREFER THE MORE GENERAL DECLARATION, NOT THE LONGER STRING

The polymorphic decl carries the SAME contract (`ensures { result = Map.set m k (Some v) }`) and
instantiated at `int` IS the monomorphic decl. So keeping POLY:

* type-checks every existing int use identically, with the same contract — **strictly more general,
  never weaker**;
* changes the emission ONLY for a module that registers BOTH, and every such module is BROKEN TODAY
  (it fails L3-tc), so it can only improve. **Predicted byte-diff: 0 MOVED on everything that
  currently works** — the code's own comment ("corpus modules keep the fixed `map int (option int)`")
  is the reason to expect that, and it is a testable prediction, not an argument.

A REFUSAL on the clash (the alternative) would be byte-inert and fail-closed but would convert a type
error into a refusal — no gain for the user and no progress on the seam. **Preferring the general
declaration is the repair that actually retires seam cases**, which is why it is the one to build.

Not a soundness route: the failure is a LOUD L3-tc type error, so nothing false is proved. This is a
CAPABILITY blocker, and it is the count ladder's item 1.
