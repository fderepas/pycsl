r"""Test 1847 — gen #31 WITNESS: a `#@ lemma` with NO `#@ assigns` clause is refused.

annotations.md §2.1.16: "A lemma must be `-> None` and `assigns \nothing` (ghost
discipline — erased at extraction, computes nothing), must state >= 1 `#@ ensures`, and is
not `#@ \diverges`." Five hard-error claims. Four of them were enforced. This one was
enforced ONLY for a lemma that DECLARED a frame:

    for t in contracts.get("assigns", []) or []:
        if not (… t.get("type") == "Nothing"): raise …

An EMPTY list satisfies that loop vacuously, so omitting `#@ assigns` entirely was the one
way past the rule. Found by taking each hard-error sentence in the documentation and
writing the program it describes — the same move that produced the `#@ mixin`,
`#@ thread_entry`, `#@ releases` and `#@ reveal` findings the same day.

NOT A SOUNDNESS HOLE, and the negative probes are worth recording because they are what
makes that claim rather than a hope. A frameless lemma that actually MUTATES is still
caught, one layer down and with a less direct message:

  * writing a module global      -> refused ("writes g through a `global` declaration")
  * writing a list PARAMETER     -> FAILS (the emitted frame obligation is unprovable)

So what was missing is the DIAGNOSTIC, not the check. `#@ assigns \nothing` on a lemma is
the ghost discipline written down, and a lemma that never says it leaves the reader to
infer it from an unprovable frame goal.

REFUSED AT `_run_pipeline`, NOT IN `_check_lemma` WHERE IT BELONGS, and the reason is a
measurement rather than a preference. `_check_lemma`'s mirror twin is UN-TRUSTED, so its
text is emitted verbatim and must PROVE — and BOTH natural spellings broke the self-proof:
`if not (contracts.get("assigns", []) or []):` puts an `or`-defaulted `.get` on a
heterogeneous dict into boolean context, and a counter incremented in the existing loop
broke it too, at the UNTOUCHED pre-existing line `if not (contracts.get("ensures") or [])`
(`This expression has type 'mu -> option.Option.option int, but is expected to have type
int`) — adding a use of `contracts` moved the dict's inferred value type and took a
neighbouring line down with it. The self-hosting constraint doing its job: the compiler may
not grow a line it cannot verify about itself. `_run_pipeline`'s twin is `\trusted` and
already in the raises-honesty population, so the choke-point rule applies.

ORDERING, VERIFIED: `_check_lemma` runs first, so `1731` (`-> int`), `1733` (`\diverges`)
and `1747` (no `ensures`) — the three existing lemma witnesses, none of which carries
`#@ assigns` either — still refuse with THEIR OWN messages, not this one.

Control: 1848, the same lemma WITH `#@ assigns \nothing`, which verifies.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ lemma
#@ requires a >= 0 and b >= 0
#@ ensures a + b >= 0
def sum_nonneg(a: int, b: int) -> None:
    pass
