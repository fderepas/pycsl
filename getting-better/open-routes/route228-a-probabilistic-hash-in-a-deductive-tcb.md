# ROUTE #228 — A PROBABILISTIC HASH IN A DEDUCTIVE TCB (Sev-1, LIVE, gen #33, 2026-09-28)

    import struct
    #@ ensures \result == 1
    def go() -> int:
        a = struct.pack('<bb6x', 1, 2)                    # CPython:  8 bytes
        b = struct.pack('<xxxxxxxxhxLxxxxxxxx', 1, 2)     # CPython: 23 bytes
        if len(a) == len(b):
            return 1
        return 0

**`[+] Verification SUCCESS! All contracts formally proven.`** — `Valid (0.00s, 156 steps)`.
CPython returns **0**. The proved postcondition is FALSE.

## THE CARRIER IS THE CAMPAIGN'S OWN ARTEFACT (order 2)

`module6_whyml/identifiers.py::stable_hash` was introduced BY this campaign, to replace Python's
`hash()` because `hash()` randomises `str` hashing per process and made WhyML emission
non-reproducible — it exists to serve the byte-diff reproducibility gate. Its docstring states the
property it preserves:

>>> "while preserving the distinguishing property (**distinct strings -> distinct ints w.h.p.**)"

**`w.h.p.` — with high probability. That is a PROBABILISTIC premise load-bearing in a DEDUCTIVE
verifier's trusted computing base**, and it is the whole of the justification. It is not a lemma, it
is not checked, and nothing in the pipeline notices when it fails.

    stable_hash(s) = int(sha256(s)[:8], 16) % 2147483647

SHA-256 truncated to **32 bits**. A birthday collision is ~2^16 trials, i.e. **under one second of
compute** — and the `% (2^31-1)` fold additionally makes `h` and `h + 0x7FFFFFFF` collide
DETERMINISTICALLY. Measured, hashing the RAW string: `'f9r'` and `'6xb'` both give `122473869`,
found after 46067 three-character candidates. Hashing the QUOTED WhyML form (which is what the
emitter actually folds): `'ah02'` and `'atc3'` both give `185314078`, after 78174.

## WHY IT IS EXPLOITABLE HERE AND NOWHERE ELSE I TESTED — THE DISCRIMINATOR IS DETERMINISM

A folded string becomes an `int` argument. That is only a FALSEHOOD if the model can then CONCLUDE
something from two folds being equal, which needs the receiving symbol to be a **pure** `val
function`. Every destination I tested first is a bare `val`, which in Why3 is non-deterministic, so
the collapse concludes nothing:

| destination | pure? | verdict |
|---|---|---|
| `val tag (s: int) : int` (a `\trusted` stub with an UNDECLARED param) | no | `(pick 185314078) = (pick 185314078)` emitted for two distinct literals, **and the proof STILL fails** — and so does its non-colliding control. **VACUOUS: that shape measured nothing.** |
| dict keys (`d["ah02"] = 1`) | — | **faithful native `string`**, no fold. Not reachable. |
| list literal `["ah02", "atc3"]` | — | **faithful native `string`**, no fold. Not reachable. |
| set literal `{"aa","aa"}` | — | correctly DEDUPLICATED (`len` -> 1, matching CPython; `{"ah02","atc3"}` -> 2). Not a route. |
| `val getattr_<cls>_poly (x: <cls>) (f: int) : 'a` | no | key is `stable_hash(field_name)`; bare `val`, concludes nothing. |
| **`val function struct_{pack,unpack}_<slot_id> (fmt: int) ...`** | **YES** | **LIVE.** |

`struct.pack` / `struct.unpack` lower to a **`val function`** — chosen deliberately, and the comment
says why: *"`val function` — both program-callable and a logical symbol the round-trip axiom can
name."* So the format string survives into the model ONLY as the folded `fmt: int`, and two
applications with the same `fmt` are **the same logical term**.

And the population of formats sharing one symbol is effectively UNBOUNDED, which `slot_id`'s own
docstring states outright:

>>> "Encodes only the slot types (**not prefix, not pad**), so two format strings that pack/unpack
>>> the same shape share the same abstract symbol. `'>IHHHHHII10Ixx'` and `'<IHHHHHII10I'` both
>>> give id `i18`."

Arbitrary pad runs (`x`, `xx`, `6x`, …) in arbitrary positions, and any byte-order prefix, all keep
the same symbol while changing the bytes CPython produces. Brute force over that space found **three**
colliding pairs immediately, all keyed `('i2', None, None, 2)`:

    '<xb3xh8x'      vs  '<3xBxxxxxB6x'            hash 1266333708   (15 vs 16 bytes)
    '<hxxxxxxxb3x'  vs  '<6xhxxxxI4x'             hash 1055455982   (13 vs 20 bytes)
    '<bb6x'         vs  '<xxxxxxxxhxLxxxxxxxx'    hash 1322019588   ( 8 vs 23 bytes)

Emitted, for the third pair — **ONE TERM FOR TWO FORMATS**:

    let a = (struct_pack_i2 1322019588 1 2) in
    let b = (struct_pack_i2 1322019588 1 2) in
    if ((Array.length a) = (Array.length b)) then …

## THE CONTROL FIRED, SO THIS IS NOT VACUOUS

Identical program with `'<hL'` in place of the colliding second format (hashes differ; CPython 8 vs
6 bytes): **`1 goal(s) remain unproven`**, `Timeout (30.00s)`. The provability comes from the
collision and from nothing else.

## WHAT IS AND IS NOT WRONG

The hash is sound **if and only if it is injective on the string literals a given program folds.**
That is a CHECKABLE property of one emission, and the emitter is the only thing that knows all the
folds — yet nothing checks it. The fold sites that produce a VALUE (as opposed to a symbol NAME) are:

    expressions.py::_coerce_str_arg      (struct fmt; "for abstract val arguments")
    expressions.py::_coerce_to_int       (string literal -> hash, int-expected positions)
    expressions.py::_str_operand_to_int  (string vs genuine int; literal folds, non-literal -> str_hash_op)
    expressions.py:12272                 getattr_<cls>_poly's field key

## THE REPAIR — MAKE THE PROBABILISTIC PREMISE A CHECKED ONE

Do NOT widen the hash. More bits lowers the probability and keeps the premise probabilistic, which
is route #227's lesson in a new costume: *an opaque answer to a wrong value moves the falsehood
rather than removing it.* The premise must become a **measurement**, fail-closed:

**Record every (original string -> folded int) at every VALUE fold site of one emission, and REFUSE
the file when two distinct strings share a fold.** Injectivity on the actual literal set is exactly
the premise; it is one dict and one comparison; and it is the honest shape — a check, not an
argument.

**THE GUARD'S POPULATION IS EMPTY ON THE WHOLE CORPUS**, so by the campaign's own rule it will look
exactly like a guard that passed while doing nothing. It MUST be negative-tested by feeding it this
route's colliding pair, which is why that pair is recorded above rather than merely counted.

**Named reopening capability, NOT required for soundness:** give `struct_{pack,unpack}_*` a faithful
`fmt: string` parameter instead of the folded int, so distinct formats are distinct terms by
construction. That touches the cited round-trip axiom signatures in `preamble.py` and every struct
corpus program's emission, so it is a COST/SCALE item, not a soundness one, once the refusal lands.

## REPRODUCE

    getting-better/open-routes/route228-collide-stable-hash.py      # finds the pairs from scratch
    getting-better/open-routes/route228-witness.py                  # the witness (PROVES, CPython 0)
    getting-better/open-routes/route228-control.py                  # the control (does NOT prove)
