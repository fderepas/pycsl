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
