# The conversion screen, first 106 of 456 — what actually stops a `\trusted` stub

A record of the first 106 results from `$SCRATCH/g31/screen_all.sh`, which converts each
still-`\trusted` mirror stub ALONE on a copied tree (live body verbatim, the stub's own `#@`
clauses untouched, only the `\trusted` line deleted) and runs emit + typecheck (`--no-proof`).
The run was cut short at 106 when the driver session's shell died; the results stand.

**Nine reported LOWERS. Seven survive a wider failure filter** — the screen's original filter
did not grep for `syntax error`, and `Module2_Parser::_parse_atom_name` and `::_parse_contract`
both emit `raise (Return {  })`, an empty record literal Why3 cannot parse.

    LOWERS (7)
      Module6_WhyMLTranspiler.py   __init__              (file proof 40m43s — unproven)
      Module6_WhyMLTranspiler.py   _emit_funcs                                  unproven
      audit_proof_reverify.py      _cache_root           **CONVERTED AND PROVED, 28 s**
      errors.py                    message               **CONVERTED AND PROVED, 11 s**
      frontend/Module2_Parser.py   _parse_quantifier     (file proof 15m12s — unproven)
      frontend/Module2_Parser.py   _try                                         unproven
      frontend/Module2_Parser.py   parse_contract                               unproven

## What stops the other 97, by category

**TYPE errors — the int-placeholder chain, and it is the plurality.** The mirror stub's
signature was written with `int` where the live one has a record, a string, a sequence or an
AST node, so the converted body's first real operation mistypes:

    but is expected to have type int                     the bare placeholder
    ... to have type string                              a `str` the stub calls `int`
    ... to have type array.Array.array                   a `List[...]`
    ... to have type seq.Seq.seq int                     a `seq`
    ... to have type PyCSL_Program.emit_ir               an IR node
    ... to have type string -> option.Option.option int  a map
    unbound function or predicate symbol '_match_block_hdr' / 'toks' / 'i'
                                                         a callee or local the stub erased

**REFUSALS — and there are more kinds than the backlog had.** Each is a deliberate,
well-worded rule, not a gap:

    `x.update(...)` / `.pop(...)` / `.extend(...)` / `.sort(...)` MUTATES its receiver in
        place, and no certified lowering models it                     — the 104-function
        item, on LOCALS as well as self fields
    `self.<field>.append(...)` appends to the collection in the field  — the known one
    in-place `append` to list PARAMETER                                 — a third receiver kind
    a function, method or class NAME is rebound after its definition
    nested function '<f>' is lifted to a sibling of its enclosing function
    function '<f>' binds <x> with a `with ... as`
    heterogeneous list literal (contains a record)

## What the distribution says

Two mechanisms account for nearly all of it: **the stub's own placeholder ANNOTATIONS**
(which the backlog has named as the #1 blocker since gen #30, and which the type-error rows
confirm at scale), and **the in-place mutators** (one refusal, measured at 104 of the 435
functions). Everything else — nested `def` lifting, `with ... as`, name rebinding,
heterogeneous literals — is a long tail of single-digit counts.

The useful consequence: a conversion attempt that begins by re-typing the stub's signature
is starting in the right place, and one that begins anywhere else is not. The screen makes
that judgement cost seconds per candidate instead of the file's whole-file proof time —
which ranges from 14 s to 2h57m across the mirror.
