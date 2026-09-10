# STAGED — the ROUTE #59 repair (built, fully measured, NOT landed)

`route59-refuse-mutated-dict-alias.patch`, generated against `7cb5bbdc`.
Two files, +86 lines, no deletions.

## WHAT IT DOES

Refuses a **mutated** dict alias in `_handle_assign_stmt`: `b = a` (or `b = self.d`) where
a later statement STORES through either name. Python binds a second name to the SAME dict,
so the store is visible through both; PyCSL models a dict as a pure Why3 map in a `ref`, so
the assignment lowers to `let b = ref !a` — a COPY — and the store is invisible.

At HEAD `a = {1:1}; b = a; b[1] = 2; return a[1]` PROVES `\result == 1`. CPython answers 2.

## WHY IT IS GATED ON A MUTATION, AND WHY THE FIRST CUT WAS WRONG

Without a store, an alias and a copy are INDISTINGUISHABLE, so a read-only rebind is sound
and must not be refused. The first build refused *every* `x = <dict>` — the corpus byte-diff
was CLEAN and the **mirror still died**, because `module6_whyml/types.py` does
`rmap = self._module_method_return_types` followed only by `rmap.get(...)`. That is route
#57's second-population lesson arriving on schedule, and it is why the gate exists.

## WHY NOT "JUST SHARE THE REF", WHICH IS WHAT THE CORRECT LIST CASE DOES

A dict local is REBOUND with the same syntax it is aliased with. `b = a; b = {2: 2}` leaves
`a` untouched in Python; sharing one ref would write THROUGH to `a`, trading an unsound READ
for an unsound WRITE. The list model escapes this only because a Why3 `array` binding is
never reassigned via `:=` — measured, list rebind-after-alias is UNDECIDED in both
directions, not wrong. Refusing is the only shape that does not open a second hole.

## MEASURED — ALL OF IT, ON THIS TREE

    the four BROKEN carriers            all now REFUSE
      b = a;  b[1]=2;  read a             (local -> local)
      b = a;  a[1]=2;  read b             (SYMMETRIC)
      a -> b -> c;  c[1]=2;  read a       (CHAINS)
      b = self.d;  b[1]=2;  read self.d   (FIELD carrier)
    the read-only rebind                 still EMITS (mirror types.py)
    controls, all UNAFFECTED              list aliasing (true PROVES / false fails),
                                          list callee-mutation, dict callee-mutation,
                                          dict-literal duplicate keys
    CORPUS byte-diff                      923 = 923, **0 differing**
    MIRROR emission                       53 = 53, exactly **2 files moved**
    plane battery                         **1 of 18 RED**, and it is the pre-existing
                                          mirror-sync pair the staged-L1 patch repairs
    why3 --type-only, all 53 mirrors      CLEAN (zero non-warning lines)
    metric                                markers 457, UNCHANGED

## THE THREE PLANES THE FIRST BUILD BROKE, AND HOW EACH WAS FIXED

Recorded because they are the reusable part:

  * `check-mirror-coverage` 552 > 550 — the build added a live-only helper method with no
    mirror counterpart. **Fixed by INLINING the walk**, no new `def` anywhere. This is the
    hazard the handoff already warned about from route #58's first build, and it still
    caught me.
  * `check-mirror-signature-drift` 1 > 0 — the build added a `rest=None` parameter to
    `_emit_first_assign`, whose mirror `\trusted` stub still had the old signature.
    **Fixed by moving the guard into `_handle_assign_stmt`**, which already has `rest`.
  * `check-trusted-raises-honesty` 71 > 70 — the live method now raises, and a `\trusted`
    stub with no `#@ raises` ASSERTS ITS LIVE COUNTERPART CANNOT RAISE. **Fixed by
    declaring `#@ raises PyCSLSemanticError when True` on the mirror stub**, which is the
    honest direction: the plane wants the declaration, not a quieter build.

## WHAT LANDING OWES, AND WHY IT IS STAGED

**TWO whole-file mirror re-proofs**, one per moved emission:

    module6_whyml/statements.py        the `#@ raises` marker itself
    Module6_WhyMLTranspiler.py         a CALLER of `_handle_assign_stmt` — its VCs change
                                       because the callee now declares it can raise

The emission delta is minimal and readable: exactly one `raises { PyCSLSemanticError -> true }`
clause per affected declaration.

It is staged rather than landed because `w52c_statements` was proving `statements.py` at
the time, to discharge a DIFFERENT debt (the `_wrap_body_with_return_catch` re-sync).
Landing mid-proof would not corrupt that run — it has already emitted — but it would make
its rc attest to the pre-patch tree while appearing to attest to the post-patch one, the
attribution loss that cost route #42 a bisect. It would also throw away a ~5-hour proof.

**SEQUENCE: collect `w52c_statements` -> apply this patch -> re-prove `statements.py` AND
`Module6_WhyMLTranspiler.py` -> land only if both are rc=0.** The reference suite is also
owed, though the corpus emission being byte-identical means its result is already
determined.
