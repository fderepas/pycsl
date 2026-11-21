# The whole conversion frontier, measured: 230 type errors, ~60 refusals, and four walls

Generation #31, 2026-09-25T20:40Z. Every live `\trusted` marker with a live counterpart has
now been ported, converted and emitted at least once. This is what the emitter said.

## The verdict distribution over every screen this session

    230   Why3 TYPE error
     ~60  REFUSED by a named emitter guard
     ~30  PORT + LOWER   (of which 14 landed, the rest refused by check 0/1 or the prover)
      6   SYNTAX
      5   higher-order argument (`cannot be applied`)

## The 230 type errors, by the type the emitter EXPECTED

    105   int
     39   string
     27   array.Array.array
     21   PyCSL_Program.<a record type>
      7   (message truncated by the screen's column limit)
      5   unbound symbol — `toks`, `self`, `ctx`
      4   array.Array.array string | array.Array.array int
      3   seq.Seq.seq int
      2   string -> option.Option.option   (a `Dict[str, V]` codomain)
      2   ref

**`int` and `string` together are 144 of 230 — 63%.** And both directions appear in every
population screened: `int` where `string` is wanted AND `string` where `int` is wanted. That
is not a missing coercion; it is a value model that carries a Python `str` as a Why3 `string`
in parameter and return position and as an `int` in record-FIELD position, so every function
moving a string across that boundary collides in whichever direction it crosses.

The 27 `array` and 3 `seq` are the same defect for a list-typed field. The 21
`PyCSL_Program.<record>` are a class the model knows by a different name than the caller uses.

## The ~60 refusals, by the guard that fired

    ~35   `X.append` / `.extend` / `.pop` / `.setdefault` / `.clear` / `.update` MUTATES its
          receiver in place, and no certified lowering models it
      9   a function, method or class NAME is rebound after its definition
      5   heterogeneous list literal (contains a str element and an int element)
      4   reassigning an array LOCAL from a non-literal
      4   nested function lifted to a sibling, and the lift is not faithful
      3   Subscript assignment to a non-array
      2   `except` can be reached
      2   `deque(<iterable>)` with arguments

Each of these is a REAL guard that exists because a previous generation measured the unsoundness
it prevents. None of them is a bug; all of them are capability boundaries with a name.

## So the four walls, sized

| wall | witnesses | what retires it |
|---|---|---|
| the **FIELD value model** (`str` and `list` as record fields) | ~174 | a faithful string/list field carrier |
| the **in-place mutator** | ~35 | a certified list/dict/set mutator lowering for a receiver |
| **dynamically-rebound names** | 9 | a name-binding model, or a refusal that is narrower |
| **higher-order arguments** | 5 | a callable value model |

Plus the two already named in the backlog — the **nested-closure lift** (#54) and the **I4
bridge re-typing** (#55) — which are emitter-internal rather than value-model.

**One capability covers three quarters of the frontier**, and it is the one
`errors.py::__str__`'s own marker comment named before any of this was measured:

> REOPENING CAPABILITY, and it is a VALUE-MODEL one rather than an annotation: the
> string-typed self fields (`filename`, `stage`) are carried as ints in the record model. A
> faithful string field model retires this marker AND several others.

"Several others" is **174**.
