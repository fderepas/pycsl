# Known Why3 Library Quirks

Load when modifying Module 6 emission paths or debugging
unexpected prover failures (especially OOMs or
type-mismatch errors).

These are non-obvious Why3 facts that affect how PyCSL generates WhyML. Keep them in mind when modifying Module6 or debugging prover failures.

| Fact | Notes |
|---|---|
| `map.Const` exports `const`, not `Map.const` | Use `(const 0)` for empty dict, `(const false)` for empty set |
| `list.Nth` returns `option 'a` | Use `list.NthNoOpt` instead — exports `nth: int -> list 'a -> 'a` with direct axioms `nth_cons_0`/`nth_cons_n` that Alt-Ergo can instantiate |
| `list.Mem` predicate is recursive | `\mem(x, l)` in loop invariants OOMs on both Alt-Ergo and Z3. Use `\nth(log, 0)` for head-tracking. When `\mem` is needed, PyCSL emits `axiom mem_head` to give the prover the head-match instantiation |
| `fun (x: T) ->` in spec context | Why3 requires parenthesised parameter in lambda expressions used in invariants/specs |
| `forall x: T. body` separator | Use `.` not `,` as the body separator in Why3 quantifiers |
| Array mutation: `a[i] <- v` | NOT `a.(i) <- v`. In program context: `a[i] <- v`. In spec context: `a[i]` for read |
| Ghost arrays are not refs | `let ghost snap = Array.make n 0` (no `ref`). Access: `snap[i]` (no `!`) |
| `string.String` has no `^` operator | Use `concat s1 s2` (not `String.(^) s1 s2`). `String.length` is still the correct length function |
| `Nil : list 'a` is polymorphic | When a `ghost_list` var is initialized with `\nil` and never used with integer ops, Why3 can't infer `list int`. PyCSL emits `(Nil: list int)` to fix this |
| `\has_key(d, k)` is option-type | Emits `Map.get !d k <> None`. Ghost dicts use `map int (option int)` — a stored value of 0 is **present** (`Some 0`), not absent. Use `\map_remove(d, k)` to remove a key. |

## Emission determinism (a class of bug)

PyCSL is an **output-deterministic** verifier: the same source must emit byte-identical WhyML on every
run and machine, because the emission-identical byte-diff gate (refactors must not change the `.mlw`) and
reproducible builds depend on it. The recurring bug that breaks this is one underlying mistake:
**anything that flows into emitted output must be ordered by *content*, never by Python set/dict-hash
iteration order.** CPython randomizes `str` hashing per process (`PYTHONHASHSEED`), so iterating a
`set[str]` — or hashing a string with the built-in `hash()` — yields a different order/value each run,
and that leaks straight into the `.mlw`.

Rules when touching any emission path (Module 5/6, inlining, SCC):

- **Iterate sets/dicts in `sorted()` order whenever the order affects emitted output** — declaration
  order, fresh-name (`__inlN`, temp) numbering, clause order. Sort by *content* (the name/key strings),
  which is what `sorted()` on `set[str]` does — not by `id()` or hash. A `set` used only for membership
  is fine; a `set` whose iteration *drives output* is not.
- **Never use the built-in `hash()` for an emitted value** — it is per-process randomized. Use the
  deterministic `stable_hash` (`module6_whyml.identifiers`, sha256-based) for any string→int lowering.

Three real instances, all fixed in `1a6b3c9` — keep them as the cautionary pattern:

1. `scc.py` — Tarjan's `strongconnect` iterated callees as a `set` → SCC tie-breaking, hence
   function-emission order, varied.
2. `ir_inline.py` — built the `__inl<N>` rename map over `_assigned_locals` (a `set`) → the `__inlN`
   suffix numbering varied.
3. `expressions.py` / `statements.py` — lowered opaque strings via `hash()` → the emitted
   `decode`/`str_hash` constants varied.

**How to catch it:** regenerate the same file 4–5× and diff the `.mlw` (`--keep-mlw`); identical = good.
One regen is *not* enough — the randomization is across processes, so a single run can look stable by
luck (this exact trap masked the codec non-determinism initially).
