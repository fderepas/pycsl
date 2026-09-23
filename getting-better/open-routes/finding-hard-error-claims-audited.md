# FINDING (#49, gen #31) — an audit of every "hard error" sentence in annotations.md

**METHOD.** `grep -nE 'hard error' test-suite/annotations.md` returns eight sentences, and
several of them bundle more than one rule. For each, write the program the sentence
describes and run it. Nothing clever; the value is that the documentation had never been
executed as a specification.

**RESULT: 9 claims tested, 7 enforced as written, 2 not.** One is repaired in the same
session; the other is recorded with its blast-radius question open.

| claim (annotations.md) | program | verdict |
|---|---|---|
| §2.1.16 a `#@ lemma` must be `-> None` | lemma returning `int` | REFUSED ✓ |
| §2.1.16 a `#@ lemma` must state >= 1 `#@ ensures` | lemma with none | REFUSED ✓ |
| §2.1.16 a `#@ lemma` is not `#@ \diverges` | both markers | REFUSED ✓ |
| §2.1.16 a `#@ lemma` may not call a `\trusted` function | lemma calling one | REFUSED ✓ |
| §2.1.16 a `#@ lemma` must be `assigns \nothing` — DECLARED frame | `#@ assigns g` | REFUSED ✓ |
| §2.1.16 a `#@ lemma` must be `assigns \nothing` — NO clause at all | no `#@ assigns` | **ACCEPTED — repaired, witness 1847 / control 1848** |
| §2.5 each `except` name in a `#@ happy` must be a real method | a typo'd name | REFUSED ✓ |
| §2.4 an `#@ act` body line must be indented exactly 4 spaces | 2-space body | REFUSED ✓ |
| §12 "a missing or EXTRA constructor is a hard error" — EXTRA | a constructor not in the `#@ datatype` | REFUSED ✓ |
| §12 the same sentence — MISSING | one constructor omitted from the `match` | **NOT a hard error — see below** |

## THE ONE REPAIRED

`_check_lemma` enforced the frame rule with

```python
for t in contracts.get("assigns", []) or []:
    if not (… t.get("type") == "Nothing"): raise …
```

and an empty list satisfies that loop vacuously, so omitting `#@ assigns` entirely was the
one way past the rule. Repaired by counting inside the loop that already walks the list.
**Not a soundness hole**, and the probes that establish that are part of the record: a
frameless lemma that actually mutates is still caught one layer down — writing a module
global is refused outright, writing a list PARAMETER makes the emitted frame obligation
unprovable and the file FAILS. What was missing was the DIAGNOSTIC.

A second lesson came out of the repair and is in `wall-lessons.md`: the obvious spelling
`if not (contracts.get("assigns", []) or [])` puts an `or`-defaulted `.get` on a
heterogeneous dict into BOOLEAN context, and since this function's mirror twin is
UN-TRUSTED, the live text must PROVE — the whole-file re-proof rejected it at once with
`This expression has type 'mu -> option.Option.option int, but is expected to have type
int`. An integer counter stays inside the modelled fragment.

## THE ONE LEFT OPEN

A `match` over a `#@ datatype` that OMITS a constructor is not a hard error. Measured on a
three-constructor type with one arm deleted:

```
Warning: Non-exhaustive pattern matching, asserting `absurd'
Sub-goal unreachable point of goal f'vc.
[-] 1 goal(s) remain unproven
```

Why3 fills the gap with `absurd` and the resulting unreachability VC is unprovable, so the
behaviour is **fail-closed and sound** — the file cannot verify. What the user gets is
"unreachable point" instead of "your `match` is missing `Empty`". The EXTRA-constructor
half of the same sentence IS a hard error (`a match pattern in this module is not
interpreted…`), which is why the sentence reads as though both were.

NOT repaired here, deliberately. The refusal would have to distinguish a genuinely
non-exhaustive match from the shapes that are legitimately partial — guards, or-patterns,
a `case _` wildcard, a match followed by a fall-through `return` — and the blast radius
across the corpus's datatype drivers has not been measured. A refusal landed without that
census is exactly lesson (d3). The capability is named so the next window can price it:
**`core_ir_semantic` already knows each `#@ datatype`'s constructor set and the IR carries
the match arms; the check is a set difference, and the cost is the census, not the code.**

Measured 2026-09-23.
