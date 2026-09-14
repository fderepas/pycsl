# ROUTE #110 — `_coerce_to_int` REPLACES A CALL ARGUMENT WITH THE LITERAL `0` when the
# lowered argument's text happens to start with an internal op spelling, and SEVEN of those
# spellings are ordinary Python identifiers a user is free to choose

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED. Repair NOT yet landed.**
**Severity: SEV-1.** A false postcondition is PROVED, and the trigger is a FUNCTION NAME.

## PROVENANCE

Found by the **substring-census** generator banked by gen #20 and run by gen #21:

>>> **A GUARD IMPLEMENTED AS A SUBSTRING TEST OVER GENERATED TEXT IS KEYED ON SPELLING, NOT
>>> ON STRUCTURE, AND THE SPELLING IS ATTACKER-CHOSEN THE MOMENT A USER NAMES A VARIABLE.**

Route #107 was the first instance anybody looked at. This is the census's top hit, and it is
**sharper than #107**: it is not in control flow but in ARGUMENT COERCION, and the erased
thing is a VALUE rather than a block.

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/expressions.py:1016-1027`

```
1016        stripped = whyml_str.strip()
1017        array_prefixes = ("(Array.make", "(Array.sub ", "(array_slice ", "(sorted_1 ",
1018                          "(list_new_arr ", "(any_1 ", "(all_1 ")
1019        for prefix in array_prefixes:
1020            if stripped.startswith(prefix):
1021                return "0"
1022        # Map-shaped expressions ...
1023        map_prefixes = ("(map_update_some ", "(map_update_none ",
1024                        "(const (None: option int)")
1025        for prefix in map_prefixes:
1026            if stripped.startswith(prefix):
1027                return "0"
```

`whyml_str` is the LOWERED WhyML for a call argument. The intent is "an array-shaped or
map-shaped term cannot be passed where an `int` is expected, so substitute a placeholder".
The test for "array-shaped" is **the first characters of generated text**.

**Seven of those prefixes are ordinary identifiers**: `array_slice`, `sorted_1`,
`list_new_arr`, `any_1`, `all_1`, `map_update_some`, `map_update_none`. `whyml_ident` leaves
each of them unchanged, so an ordinary user call `any_1(x)` lowers to `(any_1 x)` and matches
`"(any_1 "` exactly. (`(Array.make` and `(Array.sub ` are NOT reachable — a Python identifier
cannot contain a dot.)

## BOTH DIRECTIONS MEASURED at HEAD `fb69f158`

**Direction 1 — the false claim PROVES.** `d_any1.py`:

```python
#@ requires x0 >= 0
#@ ensures \result == x0 + 1
#@ assigns \nothing
def any_1(x0: int) -> int:
    return x0 + 1

#@ requires x >= 0
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    xs = [any_1(x)]
    return xs[0]
```

`[+] Verification SUCCESS! All contracts formally proven.` (rc=0.)
CPython returns `x + 1`, which is **>= 1** under the precondition, never 0.

The emitted body, read in full, shows the call is GONE — not mis-modelled, ERASED:

```
  let f (x: int) : int
    requires { (x >= 0) }
    ensures  { (result = 0) } (* linear *)
  =
    let xs = (let _alit = Array.make 1 (0) in _alit) in
    xs[0]
```

**Direction 2 — rename the callee and the SAME claim correctly FAILS.** `d_ctl.py` is
byte-identical except `any_1` is spelled `anyq_1`:

```
rc=1 — [-] Verification FAILED or INCOMPLETE.
    let xs = (let _alit = Array.make 1 ((anyq_1 x)) in _alit) in
```

The argument survives, `xs[0]` is `x+1`, and `ensures \result == 0` is refuted. So the proof
in direction 1 is caused by the SPELLING and by nothing else, and the instrument is not
vacuous: the control PROVES nothing and refuses for the RIGHT goal (the postcondition).

## WHY THIS IS WORSE THAN #107

#107 needed a `try/else`, a construct that occurs **five times in all four trees**.
`_coerce_to_int` is on the hot path of **list literals, dict keys and values, subscript
stores, `setattr`, `for`-loop iterables and abstract-op arguments** — twenty-plus call sites.
The population is not exotic.

## REPAIR SKETCH (to be RE-DERIVED before landing, per the #95 rule)

The decision is "is this term array-shaped / map-shaped", which is a **TYPE** question, and
the emitter already knows the answer structurally — the coercion must be driven by the
argument's IR type, not by the first characters of its lowering. Failing that, the internal
op spellings must be moved into a namespace `whyml_ident` provably cannot produce (the prime
trick used by the #107/#108 repair: a Python identifier cannot contain `'`), so that no
user-chosen name can ever collide. **And the substitution must never be silent**: replacing a
value with `0` is exactly the "completeness fix that supplies a WITNESS value" shape the
campaign has already been burned by five times — if the term genuinely cannot be coerced the
emitter must REFUSE, not invent a `0`.

## STILL UNPROBED, SAME FUNCTION

`expressions.py:1030` — `if "," in whyml_str and whyml_str.startswith("(") and
whyml_str.endswith(")")` replaces the term with `str(stable_hash(whyml_str))`, a constant
derived from the emitter's own text. A **comma inside a string literal argument** reaches it
(`h("a,b")`). Logged as a candidate, NOT as a finding — not run to a verdict.
