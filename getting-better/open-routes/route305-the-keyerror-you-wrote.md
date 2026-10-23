# OPEN ROUTE #305 — A USER EXCEPTION CLASS NAMED LIKE A BUILTIN IS CONFLATED WITH THE BUILTIN (handler matching under no_exception)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 13; driver-reproduced on main (4/4 rc=0; CPython violates).
Witnesses `witnesses-r305/`: `class KeyError(Exception)` (NOT a LookupError) raised inside `try ... except LookupError` under
`no_exception \all` + `ensures \result == 1` proves (r25); a user `class LookupError` "catches" the builtin KeyError (r27); named
`no_exception KeyError` variant (r29); the builtin KeyError raised implicitly by `d[5]` is caught by a handler for the user's own
`KeyError` class (r30). Without no_exception the shape is refused by #175 (r31).
Mechanism: handler matching consults `exception_model.EXCEPTION_BASES` by NAME (`handler_catches`) and the WhyML exception tag is the
bare name, so the user class and the builtin share one tag and the builtin hierarchy. Emitted: `with LookupError -> ... | KeyError -> raise (Return 1)`.
A new carrier of the #75 class (a name-keyed oracle beats the user's own definition); #75's guard covers builtin functions only.
Repair direction: refuse (or give a distinct tag + the user's own bases to) any user class definition whose name shadows a builtin
exception name (or any name in EXCEPTION_BASES / the implicit-raise trigger set), and any handler/raise that names it; census also
imported-module classes with builtin names and `E = KeyError`-style aliases to user classes.
