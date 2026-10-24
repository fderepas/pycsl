# OPEN ROUTE #336 — A PARAMETER / ELEMENT ANNOTATION pycsl DOES NOT RECOGNISE FALLS BACK TO `int` (int laws proved of floats, strings, None)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 23; driver-reproduced on main (combined files rc=0; CPython violates each function — run the file to list them).
Witnesses `witnesses-r336/` (helper rt23h.py): F1_annot_fallback.py (16 functions): parameters annotated `Num: TypeAlias = float`, plain alias
`Num = float`, `type Num = float`, TypeAliasType, `Annotated[float, ..]`, Fraction, Decimal, numbers.Real, SupportsFloat, `Optional[Num]` (int union
arm), aliases of str/None/bytes, `Annotated[str, ..]`, `t: type`, `Literal[None]` (gets `requires x = 0`) all lower to `int` (e.g. `let f_fraction (x: int)`):
`x % 1 == 0` proves for 0.5, `x - x == 0` for a str under no_exception \all, `x * 0 + 1` for None; a04 (TypeAlias float). F3_param_container_elem.py (12):
element types of PARAMETERISED containers are dropped: Sequence/Collection/tuple[float, ...]/Tuple[float, ...]/MutableSequence/Deque/Mapping/Iterable
of float, List[Annotated[float]], Dict[str, Fraction], list/dict aliases -> `xs: int`-typed elements (only list[float] and Tuple[float,float] are right);
BARE-CONTAINER-INT does not cover these (they NAME an element type); --strict-bare-containers does not refuse them.
Mechanism: the "defaults to int" fallback family (e.g. _symtype_to_whyml in module6_whyml/functions.py). #325 covers module-level values only;
the same annotations on FIELDS are already R325-refused.
Repair: every annotation that is not EXACTLY recognised (resolve aliases/TypeAlias/type statements/Annotated to their target first) must not
default to int: lower to the correct type when recognised (float -> real under FLOAT-FINITE or refuse, str -> string, None -> none, element
types of every supported container constructor), else REFUSE (named refusal) or lower to a fresh abstract type with no arithmetic. Census
every int-default site in the type-lowering code.
