# OPEN ROUTE #336 — A PARAMETER / ELEMENT ANNOTATION pycsl DOES NOT RECOGNISE FALLS BACK TO `int` (int laws proved of floats, strings, None)
**Status: REPAIRED, candidate (gen #37, 2026-10-24; opened the same day), Severity 1.** Red-team round 23; driver-reproduced on main (combined files rc=0; CPython violates each function — run the file to list them).
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

## REPAIR (2026-10-24, r336b finishing executor off ebd6f814; the r336 draft committed as found b48c7f0b)
Commits: b48c7f0b (draft), 49ff7298 / 28681a0d / a84af1ca / 834f9df4 / bba6e1b4 / 3a2ba7bc + 5a4e958c `self`-operator (code), 4d5afb39 (corpus 4480-4529),
45cac885 (docs annotations §7.23 / translational §T.6.34), 231438aa (census rows), this section. Inline, no new def, ledger 3.

Probe table (full `pycsl.py`, corpus flags; CPython ground truth in each file's `__main__`; base = ebd6f814):

| shape | base | after |
|---|---|---|
| alias of float: `TypeAlias` / plain / `type X =` / `TypeAliasType` / `Annotated[float,..]` / a04 (4480-4485) | PROVED | FAIL (Why3 rejects `%` on `real`, byte-identical to `x: float`) |
| `Fraction` / `Decimal` / `numbers.Real` / `SupportsFloat` param (4486-4489) | PROVED | FAIL (erased, goal unproven) |
| `Optional[Num]` (4490), `N2 = float \| None` (4514) | PROVED | FAIL (arm `real`) |
| str alias / `Annotated[str]` / bytes alias under `no_exception` (4491, 4492, 4494) | PROVED | FAIL (= direct spelling) |
| `None` alias / `t: type` / `Literal[None]` under `no_exception` (4493, 4495, 4496) | PROVED | REFUSED (route #252, erased into `-> int`) |
| `Sequence` / `tuple[..., ...]` / `Tuple[..., ...]` / `MutableSequence` / `List[Annotated]` / list alias of float (4497, 4499-4501, 4505, 4507) | PROVED | FAIL (= `List[float]`) |
| `Collection` / `Deque` / `Iterable` of float (4498, 4502, 4504) | PROVED | FAIL (erased) |
| `Mapping[str, float]`, `Dict[str, Fraction]`, dict alias, `Dict[str, Num]`, `Dict[str, float]`, `List[Fraction]` (4503, 4506, 4508, 4515-4517) | PROVED | FAIL (element / value erased) |
| `Optional[Fraction]` (4512), `-> Fraction` (4513) | PROVED | FAIL |
| store into `tuple[float, ...]` / `Sequence[int]` / `Mapping[str, int]` param under `no_exception` (4518-4520) | REFUSED (untyped) | REFUSED `PYCSL-R336-READONLY-VIEW-STORE` (draft had made them PROVE) |
| route #337 F2 shapes (4509-4511); `self` operators (4524, 4527) | PROVED | REFUSED / FAIL / REFUSED; REFUSED `PYCSL-R337-SELF-OPERATOR` |
| controls 4521-4523, 4525, 4526 (alias float / alias str / `Sequence[int]` read and `len` / `Mapping` read / `List[Annotated[int]]` + `Tuple[str, ...]` read) | FAIL | PROVED |
| controls 4528 (fieldless `x is x`), 4529 (record param) | PROVED | PROVED |

40 base false proofs (4480-4517, 4524, 4527: the 32 red-team functions + 8 found here) -> 0. Fidelity: for the 17 alias /
`Annotated` / view shapes the emission is byte-identical to the directly spelled annotation (checked pairwise).

Design (census of the int-default sites in the type lowering: `_param_type_str`'s final `int_type`, `_symtype_to_whyml`,
`_callable_tag_to_whyml`, the return-tag lowering, `_union_arm_tag`'s opaque-payload arm (Module 6 `_record_payload_types.get(t,
"int")`), the Module 5 element readers' `int` default):
1. RESOLVE (Module 5 `visit_Module`): module aliases bound once (`TypeAlias`, `type`, `TypeAliasType`, plain alias whose names are
   all type names), `Annotated[T, ..]` -> `T`, `Sequence` / `MutableSequence` / `tuple[T, ...]` / `Tuple[T, ...]` -> `List[T]`,
   `Mapping` / `MutableMapping` -> `Dict`, `Literal[None]` -> `None`, rewritten in params / returns / annotated locals.
2. READ-ONLY VIEWS: a param whose pre-rewrite head is `Sequence` / `Mapping` / `tuple[T, ...]` may not be stored into, mutated by
   method, `+=`-ed, or passed to a non-pure-builtin call: `PYCSL-R336-READONLY-VIEW-STORE` (stamped on the def node, raised by
   `_build_function_ir`; nested defs propagate to the enclosing def).
3. ERASE (Module 6 `_reset_function_state`, the route #249 set): a param / return tag outside the lowered set (+ records, variants,
   unions, options, callables, the mirror's reflection sentinels under their `_uses_*` gates, the bare typing containers of
   BARE-CONTAINER-INT) is an erased object; a call of such a function returns an erased value.
4. ELEMENTS (Module 5 route #249 container scan): an element / key / value type the readers do not model is tagged erased.
5. UNION ARMS (`_normalize_union_annotation`, `_union_arm_tag` kept verbatim for mirror-sync): a capitalised non-record class arm is
   `Any` (route #258 erasure of the whole annotation).
Options measured: the draft as found (1+3+4) root 4 MOVED / 1 GONE, mirror 1 MOVED / 2 GONE (a `setattr` in the new code tripped
Module 3's rebinding check on the two mirrors importing the live Module 5; the `List` tag and the `TParamNode` sentinel were erased)
and 4 new false proofs left (q1 `Optional[Fraction]`, q5 `-> Fraction`, read-only view stores); final root 9 MOVED / 0 GONE.
The #325-taint narrowing was not needed (movers far below the ~80 threshold).

Blast radius (M1 vs ebd6f814; final candidate 5a4e958c): corpus root 9 MOVED / 0 GONE / 0 APPEARED (2227 base / 2269, 42 new
sources); pyref 0/0/0 (2186/2186); mirror 2 MOVED / 0 GONE / 0 APPEARED (53/53). Every mover re-proved to its label:
- 0892 (PASS): `Trigger = Tuple[str, str]` alias resolved (tuple record fields immutable) -> PROVED.
- 0962 / 0963 / 0964 / 0965 (PASS): unused `_union_ircrosscheckresult_*` decls of `Optional[Term]` (non-record `Term`) dropped -> PROVED.
- 1312 (FAIL): `Dict[Tuple[int, int], int]` key erased (`pycsl_py_in`; was `(any int)`) -> FAIL (goal).
- 2585 (FAIL): `Optional[Sequence[int]]` -> `Optional[List[int]]` arm -> FAIL (Why3 type error, identical to the direct spelling at base).
- 2592 (FAIL): `Optional[T]` (TypeVar) now erased instead of an int-payload arm -> FAIL (goal). Its docstring's "keeps its
  two-armed variant" no longer describes the emission; the claim stays unprovable.
- 3107 (FAIL): fieldless `A` param erased; `use` now `-> object` (line-neutral, docstring note) so the #278 MRO goal
  `c__m_refines_a` is still reached and FAILS (without the edit: REFUSED by route #252 before the goal).
- mirror `proof2why3/crosscheck_ir`, `proof2why3/sertop`: unused `_union_*` decls dropped; L3 whole-file proofs PROVED
  (HEAVY_SHORT, rc 0). No OWED proof.
No previously-proved corpus/pyref file now fails (no latent false proof surfaced by the movers).

Gates (rc): witnesses table above; corpus + pyref byte-diff (above); mirror-emit-sweep `--min-files 50` (above);
check-self-annotate-sync 0 (926 verbatim), self-annotate-mirror-check 0; run-soundness-planes fast 0 (61/61); check-getattr-erasure 0;
check-stdlib-modules-verify 0 (the known 21 non-verifying modules); doc-coherency --check 0; check-assumed-facts 0; check-trusted-raises-honesty 0
(61, ratchet kept by raising from the already-raising `_build_function_ir`); check-refusal-witness-coverage 0 (282 / 5 / 10, no
flags); check-dropped-mutation 0; check-corpus-contract-truth 0, -args 0; check-assigns-underdeclaration 0 (TRAP 3; the refusal
message rides on the def node, not a new emitter field). Ledger 3, no gate loosened.

Residuals: (a) `x % 1` on a float is a Why3 type error, not a refusal (pre-existing for `x: float`); `Optional[List[int]]`
parameters type-error (pre-existing). (b) Aliases are module-level only (class-body / function-local aliases, imported aliases and
generic `type X[T] = ...` are not resolved: they stay unrecognised and are ERASED, never int). (c) A bare `Sequence` / `Iterable` /
`Mapping` param is now erased (stricter than BARE-CONTAINER-INT, whose doc row was narrowed). (d) The read-only-view check is
syntactic on the parameter name (a local alias `ys = xs; ys[0] = 1` is not followed — route #289-style aliasing residual).
(e) Erased returns accept the `Iterator` / `Generator` / `Iterable` heads (generator seams); their element types are not checked here.
