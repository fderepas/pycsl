# ROUTE #75 — a name-keyed oracle beats the definition the user wrote (THE CLASS)

**STATUS: CLOSED** (found and repaired in generation #6).

**This route is the CLASS that routes #73 and #74 are instances of.** It was closed with ONE
structural guard rather than a third local patch.

## THE CARRIERS

Python lets a module SHADOW A BUILTIN. When it does, the name tests in
`_call_named_builtins` fire on the user's own function and hand the call an abstract `val`
whose `ensures` is an AXIOM about the BUILTIN's behaviour. Three carriers, each a complete
runnable program, each with its TRUE twin failing to prove:

| user definition | call | claim proved | CPython |
|---|---|---|---|
| `def ord(c: str) -> int: return 9999` | `ord("a")` | `\result < 256` | 9999 |
| `def len(x: str) -> int: return -5` | `len("ab")` | `\result >= 0` | -5 |
| `def min(a: int, b: int) -> int: return 99` | `min(1, 2)` | `\result <= 1` | 99 |

**NOT carriers, MEASURED rather than assumed: `bool`, `repr`, `hash`.**

No `no_exception`, no opt-in of any kind — the route #69 class.

## HOW IT WAS FOUND — BY ENUMERATING THE CLASS

Not by probing a third instance. A script over `expressions.py` maps every
`_add_abstract_op` carrying an `ensures` back to the nearest name test guarding it. That
yields TWELVE: `decode`, `any`, `min`, `sorted`, `list`, `ord`, `chr`, `repr`, `bool`,
`hasattr`, `get` (= route #73) and the rsplit predicate set (= route #74).

**Two of the twelve were already known routes, which is what made the enumeration worth
trusting.**

## THE REPAIR — ONE GUARD FOR THE CLASS

At the entry of `_call_named_builtins`: a BARE name that resolves to a user-defined function
falls through to it.

```python
if (isinstance(func_name, str) and "." not in func_name
        and func_name in getattr(self, "_module_method_return_types", {})):
    return None
```

**STRUCTURAL, NOT A LIST OF NAMES**, and the non-uniformity of the carriers is the argument:
`bool`/`repr`/`hash` are not carriers, so a name list would have been stepped around by the
next entry in the table — the failure mode this campaign has hit repeatedly.

**FALL THROUGH, NOT REFUSE.** All three true twins now PROVE where none did before, so the
user's own proved contracts are reachable again at three call sites.

## THE BYTE-DIFF FOUND A FOURTH CARRIER THE CENSUS MISSED

`0449` moved unexpectedly, and reading it rather than waving it through was the point. It is
a SECURITY driver proving that a `try/except` wrapper around `ast.literal_eval` is TOTAL, and
it declares `literal_eval` itself with `#@ \abstract` + `raises ValueError` /
`raises SyntaxError`. Its call site had been emitting

    val literal_eval_op (s: 'a) : int        <- AN ORACLE WITH NO CONTRACT AT ALL

instead of the user's own declaration. After the guard it emits `(literal_eval src)`.

So the class covers user `\abstract` DECLARATIONS too, not just builtins.

**VERIFIED, NOT ASSUMED:** 0449 still PASSES, and its OWN documented anti-vacuity claim still
holds — narrowing the catch to `(ValueError,)` makes verification FAIL — so the security
proof now runs against the real bounded-raises declaration rather than a contract-free oracle.

**CENSUS LESSON:** the census grepped `^def <builtin-name>(` and missed this, because the
shadowed name was `literal_eval` — not a builtin at all. **The oracle table is wider than any
name list enumerable by hand; the byte-diff over BOTH corpora is what caught it.**

## GATES

* 33 planes green; python-reference 2204/2204 byte-inert; pycsl-reference 969/969 with 7
  MOVED (six witnesses + 0449), 0 GONE, 0 APPEARED.
* Suite 3312/3331, ZERO XPASS, failure set byte-for-byte identical to baseline.
* Witnesses 1182-1187: three negatives and three positive controls.

## RESIDUAL — WHAT THIS GUARD DOES *NOT* COVER

The guard is scoped to BARE names; route #74 covers the `self.<m>(...)` spelling at its own
site. **The DOTTED oracles are still unguarded** — `func_name.endswith(".to_dict")`,
`.copy`, `.findall`, `.split`, and the class-name-keyed `IRScanner.*` / `self.ir.get`. They
were checked and **carry no `ensures` at all**, so they hold no false axiom and are
fail-closed for a result claim; they also shadow, which costs completeness. **If an `ensures`
is ever added to one of them, it becomes this route again.**
