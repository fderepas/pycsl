# Run #9 u74 report: `_to_cache_payload` converted; `parse_format` and `bases_closure` measured

Executor u74, driver run #9, self-tcb-reduction base loop.

- Branch `run9-u74` in `/home/fabrice/git/pycsl-u74`. Base = `run9-u67` **96eac515d** (main L20 + the u67 type_of_batch conversion). `ghost-assign-bc6` had no `src`/`bin`/`test-suite` change past the base when checked (15:00Z), and `main` (f552646c4) is already contained, so no merge was needed.
- Base tree (detached at 96eac515d): `/home/fabrice/git/pycsl-u74b`. Head snapshot tree: `/home/fabrice/git/pycsl-u74h`.
- Paths are relative to `scratchpad/u74/` unless absolute. Never pushed.

__STATUS__

## 1. Measured chains (QUICK `--no-proof` probes of scratch copies; `probe.sh`, variants `v/*.py`, logs `v/*.log`)

All three chains were walked at the base before anything was built. Every probe passes `--verification-image`.

### 1.1 `_to_cache_payload` (audit_proof_reverify.py): 4 links + 1 free [T]. CLOSED, converted.

| step | variant | verdict |
|---|---|---|
| verbatim port (marker dropped) | `c0` | L3-TC: bare `-> dict` is `map int (option int)`; `HStr`-less string values (`string` vs `int`) |
| [T] live+mirror return annotation `-> Dict[str, PyVal]` (runtime-inert under `from __future__ import annotations`; the `PyVal` sentinel as in Module5) | `c1` | L3-TC: `HInt report.elapsed_compile_s` (`real` vs `int`) = **link 1** |
| — after link 1 | — | TC-OK but a FACADE (cv15): `"qualname_results"` is `HInt (list_comp 0)`, input-blind. The field `qualname_results: List[tuple[str, bool, List[str]]]` is `array int` = **link 2a**; the tuple target `(qn, ok, axs)` is erased to `_comp_var` in the IR = **link 2b**; the comprehension in hval position = **link 2c** |
| all four links | `c2` | **TC-OK**, faithful (below) |

### 1.2 `parse_format` (module6_whyml/struct_format.py): ≥ 6 links + 2 live rewrites. NOT attempted.

| step | variant | verdict |
|---|---|---|
| verbatim port + [T] class sync (`slots: Tuple[str, ...]`, `chars`) | `p0` | REFUSED: `slots.extend(...)` has no certified mutation lowering |
| class sync only (stub kept) | `p1` | L3-TC: a variadic `Tuple[str, ...]` field is `array int` (erased), which also breaks the VERIFIED `slot_id` (`_short_type(self.slots[0])`) |
| [R] `slots = slots + [slot_type] * count` | `p2` | REFUSED R325: `tuple(slots)` is the opaque `tuple_1` |
| stand-in `slots=slots` | `p3` | REFUSED R551 (list passed to a tuple parameter) |
| + [R] termination guard `if m.end() <= pos: return None` + `#@ loop variant len(fmt) - pos` | `p4` | same R551 |
| stand-in class fields `List[str]` | `p5` | L3-TC: `Return__union_parse_format_0 has mutable components` (an `Optional[<record>]` return of a mutable record) |
| stand-in return `Optional[int]` | `p6` | L3-TC: the tuple assignment `count_str, char = m.group(1), m.group(2)` erases both to `int` (calcsize uses annotated single assignments); `_CHAR_TO_TYPE.get(char)` is the opaque `_CHAR_TO_TYPE_get_1 : int`; `[slot_type] * count` is an `array` of an `Optional[str]` |

Links measured: (1) list `extend` (or a live rewrite), (2) `tuple(<list local>)`, (3) a typed `Tuple[str, ...]` field as a pure `seq string` + re-proof of the VERIFIED `arity` / `slot_id`, (4) a PURE (non-`mutable`) record for an `Optional[<frozen dataclass>]` exception payload (emitter-wide record change), (5) typed tuple-assignment of `str` results, (6) `_CHAR_TO_TYPE` as an `option string` map plus the `Optional[str]` narrowing of `slot_type` (it is non-None only through `not (slot_type is None and char != "x")` ∧ `char != "x"`). Plus the [R] live termination guard: `re_end_op` is law-free, so `len(fmt) - pos` decreases only through the guard calcsize already carries (no axiom may state that the token pattern consumes a character).

### 1.3 `bases_closure` (exception_model.py): ≥ 5 links, one of them a termination proof over a finite universe. NOT attempted.

| step | variant | verdict |
|---|---|---|
| verbatim port | `b0` | REFUSED: `frontier.pop()` has no certified mutation lowering |
| stand-ins `frontier[len-1]` / slice / `frontier + list(..)` | `b1` | L3-TC; the emission shows the rest of the chain: `EXCEPTION_BASES.get(exc, ())` is the opaque int-hashed `eXCEPTION_BASES_get_2 (str_hash_op exc) ()`; `seen: set` is `map int (option int)`; `frozenset(seen)` is the opaque `frozenset_1` against a bare `frozenset` codomain (`map int (option int)`); and the `while frontier` loop has NO variant |

Termination is the deciding wall. A `while` with no variant in a non-`\diverges` function is an unprovable termination VC (checked: Why3 1.8.2 `w/t.mlw`). The only variant is `K * (|U| - |seen|) + len(frontier)` (U = the finite set of base names, K = the longest base tuple), which needs a CONCRETE model of the ~70-entry `EXCEPTION_BASES` literal, the invariant `frontier ∪ seen ⊆ U`, and set cardinality, none of which the current set model (`map int (option int)`) has. Declaring it `\diverges` would be a contract change cascading to the VERIFIED `handler_catches`' callers. So this is a capability boundary (no axiom is needed in principle, but it is not a bounded build).

**Ranking by complete-chain cost:** `_to_cache_payload` (4 links, all local, one mirror re-proof outside its file) < `parse_format` (6 links + 2 live rewrites, one emitter-wide record change) < `bases_closure` (termination over a finite universe).

## 2. Capability edits (commit cdd7db154)

__CAPS__

## 3. Mirror and contract

__MIRROR__

## 4. Proofs

__PROOFS__

## 5. Leaf reachability and mutation

__LEAF__

## 6. Red-team notes (QUICK probes, `rt/`)

__RT__

## 7. Gates

__GATES__
