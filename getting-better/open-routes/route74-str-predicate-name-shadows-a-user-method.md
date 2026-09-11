# ROUTE #74 — a str-predicate NAME match shadows a user-defined class method

**STATUS: CLOSED** (found and repaired in generation #6).

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


## THE LANDED REPAIR, AND WHAT MEASUREMENT ADDED

The guard falls through (does not refuse) when the call resolves to a user-defined method,
keyed the same way the `-> NoReturn` check already keys:
`whyml_ident(f"{self._current_self_type}__{method}") in self._module_method_return_types`.

**THE EMITTED RESULT IS THE POINT — THE FALSE AXIOM IS REPLACED, NOT MERELY SUPPRESSED:**

```
val self_isdigit_0 () : int
  ensures { (result = 7) }      <- was: ensures { ((result = 0) || (result = 1)) }
```

The stub now carries the CALLEE'S OWN verified postcondition (propagated by route #70's
machinery, since the callee has a trivial precondition). So `\result <= 1` fails because 7
is not <= 1, and `\result == 7` proves.

**A SECOND CARRIER WAS FOUND BY PROBING THE ARGUMENTS PATH.** `startswith`/`endswith` take
arguments and go down a different branch, emitting
`val self_startswith_1 (x0: int) : int ensures { ((result = 0) || (result = 1)) }`. With the
guard removed it PROVED `\result <= 1` for a method returning 9. A guard closing only the
zero-argument spelling would have left it open — witness 1180.

## GATES

* Anti-vacuity demonstrated BOTH DIRECTIONS by removing the guard: 1178 and 1180 both PROVE
  with it off, both fail with it on.
* **Positive controls, two of them:** 1179 (the user's true claim now proves) and 1181 (a
  REAL `str.isdigit()` still discharges `<= 1`, so the repair did not blanket-remove the
  predicate model — without it 1178 would pass for the wrong reason).
* Blast radius censused at ZERO before landing: no method with any of the twelve names is
  defined anywhere in `src/` or `test-suite/`.

## RESIDUAL, MEASURED RATHER THAN ASSUMED

The `obj.<m>()` spelling on a local of a user class (`c = C(); c.isdigit()`) does NOT prove.
That matches gen #5's finding that object-typed locals do not emit in any spelling — it is a
TYPE ACCIDENT rather than a guard, and it is recorded as such: if object locals ever start
emitting, this spelling must be re-measured, because the name-match branch would be reached
with `func_name` not starting with `self.` and the registry key would not be built.
