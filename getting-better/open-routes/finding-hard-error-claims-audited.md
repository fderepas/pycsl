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

## 2026-09-24 — THE CENSUS THE REFUSAL WAS WAITING ON, AND IT COMES OUT ZERO

The entry above named the cost exactly: *"the check is a set difference, and the cost is
the census, not the code."* The census is done (`$SCRATCH/g31/census_dt.py`, an AST scan of
both corpora, `src/pycsl`, `src/self-annotate/src` and `src/pycsl_lib`).

**21 `match` statements over a `#@ datatype` value, in 16 files, all in `pycsl-reference`.
NONE of them omits a constructor.** The mirror and `src/pycsl_lib` declare no `#@ datatype`
at all.

| shape | count | files |
|---|---|---|
| plain arms, subject resolved to its datatype, **complete** | 14 | 0520 0521 0528 0534(x2) 0541 0545 0555 0559(x2) 0565(x2) 0570(x2) |
| plain arms, subject NOT a directly annotated parameter | 3 | 0521 0527 0533 |
| `case _` wildcard | 1 | 0536 |
| or-pattern (`case A \| B`) | 2 | 0535 0546 |
| guard + wildcard | 1 | 0531 |

So the blast radius of the refusal is **zero corpus files**, provided it is written the way
the shapes demand:

  * a `case _` wildcard makes the match exhaustive — never refuse (0536);
  * an or-pattern is EXPANDED into its alternatives before the set difference (0535, 0546);
  * a GUARDED arm does not count as covering its constructor (0531 — which also carries a
    wildcard, so it stays green either way);
  * if the subject's type cannot be resolved, FALL THROUGH — check nothing rather than
    guess (the 3 rows above, whose subjects are locals or nested expressions). Today's
    behaviour for those is already fail-closed at Why3's `absurd`, so falling through loses
    nothing that is currently caught.

The four special shapes are purpose-built drivers for exactly those features, which is the
ideal control set: they are the files that must NOT move.

**THE REFUSAL IS NOW PRICED AT ITS CODE ONLY.** Remaining work is the set difference itself
plus the diagnostic text, at the `_run_pipeline` choke point per the standing rule, and a
witness/control pair in the corpus (a three-constructor type with one arm deleted, which
today reports `Warning: Non-exhaustive pattern matching, asserting 'absurd'` and
`Sub-goal unreachable point of goal f'vc` instead of naming the missing constructor).

### AND THEN THE CENSUS'S OWN CONCLUSION WAS REFUTED — DO NOT ADD THE REFUSAL

The paragraph above prices the refusal at "its code only" and says the blast radius is zero.
The blast radius over the CORPUS is indeed zero; the blast radius over LEGITIMATE PYTHON is
not, and one probe shows it:

```python
#@ datatype Color = Red | Green | Blue
#@ requires c != Blue()
#@ ensures \result >= 0
#@ assigns \nothing
def to_code(c: Color) -> int:
    match c:
        case Red():
            return 0
        case Green():
            return 1
```

    Warning: Non-exhaustive pattern matching, asserting `absurd'
    Prover result is: Valid (0.01s, 371 steps).
    [+] Verification SUCCESS! All contracts formally proven.

**A partial match is LEGITIMATE when the precondition rules the missing constructors out,
and Why3 discharges exactly that.** The `absurd` is not a failure mode — it is the
obligation, and it is provable when the program is right. A hard refusal on "the arm set
omits a constructor" would make this program unwritable, and it is a GOOD program: the
precondition carries the fact, the prover checks it, the match is total on its domain.

So the item is not "priced and ready"; it is **CLOSED AS WRONG**. The entry above reached
the opposite conclusion on a census of 21 corpus matches — a population that contains no
precondition-restricted partial match, because nobody has written one yet. Counting what
EXISTS says nothing about what a rule would FORBID. That is the same failure shape as the
five uncovered-directive excuses of the same day, arriving from the other direction.

WHAT IS STILL WORTH DOING, and it is a diagnostic and not a rule: when the unreachability
VC is UNPROVEN, say which constructors are missing. The information is a set difference over
the IR, exactly as priced — what changes is that it rides on the FAILURE PATH as advice,
never as a refusal, so the provable case above is untouched. Two different internal messages
currently stand in for it: `Sub-goal unreachable point of goal <fn>'vc` for the plain shape,
and `This expression has type int, but is expected to have type ()` when the omitted arm is
replaced by a GUARDED one.

Measured 2026-09-24. Probes: `$SCRATCH/g31/w/{dt2,dtreq,1874,1875,1876}.py`.
