# Review of `ghost-dictionnaries.md` — Claude

## Overall verdict

Technically sound model (`map int int` + SMT-LIB `Array Int Int` is the right choice),
but `\map_dom` is semantically broken in the chosen representation and must be dropped
from Phase 1, and the current-state table needs correction.

---

## Key strengths

- **`map int int` with `Const.const 0` default**: maps directly to SMT-LIB's
  `(Array Int Int)` theory. Z3 can discharge `Map.get (Map.set m k v) k = v` and
  related goals by symbolic simplification in under 0.01s — no quantifier instantiation
  needed for the common case.
- **`\map_get`/`\map_set` as thin wrappers**: minimal, correct, and the generated Why3
  is readable (`Map.get !d k`, `Map.set !d k v`).
- **Ref-wrapping**: consistent with ghost lists, ghost sets, ghost strings (all
  non-primitive ghost types are ref-wrapped). Correct because `map int int` is
  immutable — mutations require full substitution via `Map.set`.
- **`\empty_map` → `Const.const 0`**: correct Why3 idiom for a total map defaulting
  to 0.
- **Sharing `map.Map` + `map.Const` with ghost sets**: the plan's preamble notes this;
  a single `needs_map` flag covering both is the right implementation.

---

## Critical issues

### Issue 1 — `\map_dom` is semantically broken (must drop from Phase 1)

A `map int int` is a **total function** ℤ → ℤ. Every integer is in its domain —
`Map.get m k` is defined for all `k`. The plan defines `\map_dom` as the set of keys
"explicitly set" by `\map_set`, but there is no way to track "explicitly set" vs.
"default 0" using `Map.get`/`Map.set` semantics. The representation is
indistinguishable.

If a user writes:
```python
#@ ensures k in \map_dom(d)   # means: d[k] was explicitly set
```
the generated Why3 predicate would need to know whether `Map.get !d k` was set
intentionally or is just the default 0. This is undecidable in the chosen
representation without a separate bit-mask tracking "which keys are live."

**Fix**: drop `\map_dom` from Phase 1 entirely. Add a note: "Domain semantics require
a separate ghost boolean map (see ghost-sets.md). Use `\map_get(d, k) != 0` as an
approximation when 0 is the 'not present' sentinel."

If domain tracking is needed in the future, it requires a paired ghost set: one `map
int int` for values plus one `map int bool` for the "is-set" mask.

### Issue 2 — `_dict_locals` collision in Module6

Module6 tracks Python runtime dicts in `self._dict_locals`. Ghost dicts must NOT be
added to `_dict_locals` — otherwise they would receive the same treatment as runtime
dicts (lowered to abstract `int` values via the existing opaque dict model).

**Fix**: add `self._ghost_dict_vars: Set[str]` to `_reset_function_state`. In
`_handle_ghost_assign_stmt`, when `ghost_type == "dict"`, populate `_ghost_dict_vars`.
In Module6's dict-classification logic, gate on `name not in self._ghost_dict_vars`.

### Issue 3 — Current-state table inaccuracies

The table states "Module5 treats `SetLit` as `dict_vars`". In the current code, `SetLit`
is a distinct IR node type and goes through its own path — it is not treated as a dict.
This overstates what Module5 already handles and will cause confusion when developers
try to navigate the existing code.

Also: Module4's ghost handling "hard-coded `int`" is correct but the implication that
Module4 knows nothing about dicts is misleading — Module4 does validate dict key access
in body expressions. The table should distinguish ghost variable tracking from dict
expression validation.

### Issue 4 — `\map_eq` extensional equality not documented

`\map_eq(d1, d2)` compiles to `d1 = d2` in Why3. For `map int int`, Why3's map theory
provides extensional equality: two maps are equal iff `Map.get m1 k = Map.get m2 k` for
all `k`. This is provable by Z3 via the `map` theory axioms.

Users who expect `\map_eq` to mean "same explicitly-set keys" will be surprised when
two maps are "equal" even if they were constructed differently, as long as they agree
on all integer keys. This must be documented.

---

## Suggestions

1. Drop `\map_dom` from Phase 1. Add an explicit note explaining why: total function
   representation cannot distinguish "explicitly set" from "default 0" (Issue 1).
2. Add `self._ghost_dict_vars: Set[str]` and gate all `_dict_locals` paths on exclusion
   (Issue 2).
3. Fix the current-state table: remove the `SetLit`/`dict_vars` conflation (Issue 3).
4. Add a subsection documenting `\map_eq` as extensional equality, not "same keys"
   (Issue 4).
5. Add `_iter_csl_children` for all new dict expression nodes.
6. Update self-annotated copies when the feature lands.

---

## Suggested staging

**Phase 1 (ship this):**
- `\empty_map`, `\map_get`, `\map_set`, `\map_eq`
- Ghost dict declaration (ref-wrapped `map int int`)
- Module4 scope registration, Module5 IR field, Module6 emit
- `self._ghost_dict_vars` tracking
- `use map.Map` + `use map.Const` shared with ghost sets
- 3 reference tests (frequency table, inverse map, equality check)

**Phase 2:**
- `\map_dom` via paired ghost set (if needed) — requires ghost-sets to be landed first
- Custom default value (currently hardwired to 0)

**Defer:**
- Domain semantics (`\map_dom`) until ghost-sets plan is landed

---

## Comparison with GPT review

**Agreement:**
- GPT correctly identifies `\map_dom` as semantically problematic.
- GPT correctly says the current-state section is inaccurate.
- GPT recommends removing/replacing `\map_dom`.

**Additional issues (not in GPT review):**
- The specific `_dict_locals` collision mechanism (GPT says "existing ad hoc set
  handling should not be conflated" generically; the precise variable is `_dict_locals`).
- `\map_eq` extensional equality semantics need documentation — GPT does not mention
  this.

**Disagreement with GPT:**
- GPT says the scope is "optimistic" overall. I disagree: the plan scope is appropriate
  for a first version if `\map_dom` is dropped. The work is well-bounded: one field
  addition, one grammar rule set, IR pass-through, and a Module6 emit branch.
