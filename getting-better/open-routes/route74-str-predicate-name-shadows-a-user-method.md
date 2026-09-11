# ROUTE #74 — a str-predicate NAME match shadows a user-defined class method

**STATUS: OPEN — found in generation #6, repair scoped and censused, landing deferred only
because the reference suite was reading the tree when it was found.**

## THE CARRIER

```python
class C:
    #@ ensures \result == 7
    def isdigit(self) -> int:
        return 7

    #@ ensures \result <= 1
    def g(self) -> int:
        return self.isdigit()
```

**CPython answers `7`. PyCSL proves `\result <= 1`.**

No `no_exception`, no opt-in of any kind. This is the route #69/#73 class: a FALSE
POSTCONDITION about ordinary TOTAL Python.

## THE CAUSE

`module6_whyml/expressions.py:8861`:

```python
if "." in func_name and func_name.rsplit(".", 1)[-1] in (
        "islower", "isupper", "isalpha", "isdigit", "isspace",
        "istitle", "isalnum", "isnumeric", "isdecimal",
        "isidentifier", "startswith", "endswith"):
```

The match is on the **method-name suffix alone**, with the **receiver erased entirely**, and
`_call_named_builtins` is consulted BEFORE `_handle_dotted_call`, so the name match wins over
the user's real method.

## THE EMITTED WhyML CONTAINS BOTH, AND THAT IS THE PROOF

```
val self_isdigit_0 () : int ensures { ((result = 0) || (result = 1)) }   <- the oracle
  (self_isdigit_0 ())                                                     <- the call site
let c__isdigit (self: c) : int                                            <- the REAL method, UNUSED
```

Note the **empty parameter list** on the `val`: the receiver is gone, so nothing ties the
axiom to any object. That is the same structural tell routes #13/#14 keyed their guard on —
"an abstract op that takes neither the receiver nor a `writes` clause has had its effect
deleted" — except that this is the READ/PREDICATE version rather than the MUTATOR version,
and instead of deleting an effect it **asserts a false fact**.

Anti-vacuity verified both directions: the TRUE claim `\result == 7` does NOT prove.

## EXPOSURE

**TWELVE method names**, all ordinary English words a user class may legitimately define:
`islower`, `isupper`, `isalpha`, `isdigit`, `isspace`, `istitle`, `isalnum`, `isnumeric`,
`isdecimal`, `isidentifier`, `startswith`, `endswith`.

## HOW IT WAS FOUND

By doing the banked follow-up to route #73 — *probe one call deeper, one argument position
over, one field away*. #73 was an oracle keyed on a literal STRING shadowing a user function;
this is an oracle keyed on a method NAME shadowing a user method. The delegated `val` audit
had flagged it as a name-collision **hazard it could not witness**; the witness took one
driver.

## THE SCOPED REPAIR (censused, not yet landed)

Fall through to the real method — do NOT refuse — when the call resolves to a user-defined
method, using the same key construction the `-> NoReturn` check already uses:

```python
whyml_ident(f"{self._current_self_type}__{func_name[len('self.'):]}")
    in self._module_method_return_types
```

Falling through rather than refusing is what makes the user's own contract reachable again,
exactly as route #73's witness 1176 demonstrated.

**BLAST RADIUS CENSUSED: ZERO.** No method with any of the twelve names is defined anywhere
in `src/` or `test-suite/`, so the repair is byte-inert on both corpora and the mirror by
construction.

**RESIDUAL TO PROBE AFTER LANDING** (the #73 lesson — probe your own repair for the gap it
leaves): this closes the `self.<m>` spelling. The `obj.<m>()` spelling on a local of a user
class is believed unreachable (gen #5 measured that object-typed locals do not emit in any
spelling — a TYPE ACCIDENT, not a guard), but that is exactly the kind of accident that
stops holding, and it must be re-measured rather than assumed.
