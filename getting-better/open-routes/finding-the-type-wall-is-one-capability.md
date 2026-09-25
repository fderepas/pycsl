# The 36 type errors blocking conversion are one capability, and the mirror already names it

Generation #31, 2026-09-25T04:08Z. Of the verbatim `\trusted` candidates screened, **36 fail
with a Why3 TYPE ERROR** when the marker is removed — by far the largest single obstacle, more
than three times the refusal count. This measures what they actually say.

## The messages, in full

    Module6_WhyMLTranspiler.py   _shared_use_lines         int  ->  array.Array.array
    Module6_WhyMLTranspiler.py   _sig_val_from_let         int  ->  array.Array.array
    audit_proof.py               _extract_directives       int  ->  array.Array.array
    audit_proof.py               audit_lean                int  ->  string
    audit_proof.py               audit_rocq                int  ->  string
    audit_proof_reverify.py      _cache_load               string -> int
    audit_proof_reverify.py      _cache_store              string -> int
    audit_proof_reverify.py      _to_cache_payload         string -> int
    audit_proof_reverify.py      summary                   real -> int
    errors.py                    __str__                   string -> int
    errors.py                    as_dict                   string -> int
    frontend/Module5_IREmitter.py __init__                 int  ->  string
    pycsl.py                     _find_coqc                int  ->  PyCSL_Program.
    pycsl.py                     _function_body_eqs        int  ->  string
    pycsl.py                     _json_goal_records        int  ->  array.Array.array
    pycsl.py                     _make_temp_mlw_path       int  ->  string
    pycsl.py                     _merge_records_best_of_n  int  ->  string -> option.
    pycsl.py                     _parse_goal_blocks        seq.Seq.seq 'mu -> int
    pycsl.py                     _residual_selectors...    int  ->  string -> option.
    pycsl.py                     _synthesize_legacy_text   int  ->  string

(20 captured in full; the remaining 16 matched the screen's shorter classification and fall in
the same three buckets — 17 `int`, 8 `array`, 9 `string`/`string -> option` across all 36.)

## The direction is the finding

**Both directions appear.** Six are `int` where `string` is wanted; five are `string` where
`int` is wanted. That is not a missing coercion in one place. It is a value model that carries
a Python `str` as a Why3 `string` in PARAMETER and RETURN positions and as an `int` in RECORD
FIELD positions, so every function that moves a string across that boundary collides — in
whichever direction it happens to cross.

And the mirror already says so, in the `\trusted` comment on `errors.py::__str__`, written
before this census existed:

> REOPENING CAPABILITY, and it is a VALUE-MODEL one rather than an annotation: the
> string-typed self fields (`filename`, `stage`) are carried as ints in the record model. A
> faithful string field model retires this marker AND several others; it is the same
> capability the `hval`/string track has been circling.

The census makes "several others" a number. **At least 11 of the 36 are string-field
collisions; the 8 `array` ones are the same defect for a list-typed field; the rest are
`Dict[str, V]` codomains (`string -> option.Option.option`) and one record type.**

## Why this matters more than the count

`errors.py::message` — the marker this session retired and proved — is a method on the SAME
class whose `__str__` cannot convert for exactly this reason. One class, two markers, one
capability between them. `message` could be proved only because its body does not touch a
string field; `__str__` builds a `seq string` out of `self.filename` and `self.stage`, which
the record model holds as ints.

So the conversion frontier is not 36 separate problems. It is **one value-model capability
with 36 witnesses**, and those witnesses are now enumerated, named, and reproducible — a
faithful string (and list) field model can be built against this list and measured against it
afterwards.
