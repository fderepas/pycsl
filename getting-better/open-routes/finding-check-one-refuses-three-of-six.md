# Check 1 refuses three of the six stubs that lower — and names one mechanism each time

Generation #31, 2026-09-25T03:49Z. Six of the 56 verbatim `\trusted` candidates lower under
`--no-proof`. Two of them landed (commit `af7f32c1`). Here is why the others did not, each
established by the same instrument: **diff the emitted `.mlw` before and after retiring the
marker, and read what the `let` body actually says.**

## The two that landed

    errors.py::message              11 diff lines; ONE new `val` — `str_dunder_op () : string`,
                                    no defining axiom, exactly the opacity the old `val` had.
                                    4 frame `ensures` assumed -> proved, x4 inheriting classes.

    proof2why3/sertop.py::__exit__  11 diff lines; ZERO new `val`. The `let` body is `()` and
                                    the LIVE body is `pass`, so the model is exact.

## The three refused, and the mechanism each names

### `audit_proof_reverify.py::_cache_root` — a nullary `val` for a side effect

    val root_mkdir_0 () : int          (* nullary, NO `writes` *)
    let _cache_root (project_root: string) : string
      requires { true }  ensures { true }
    = let root = ref (path_join_op project_root ".audit-cache") in
      let _ = (root_mkdir_0 ()) in (); !root

`os.mkdir` becomes a nullary abstract op with no `writes` clause. Converting would CERTIFY
`assigns \nothing` over a directory creation. Refused.

### `ir_schema.py::validate_ir` — twenty nullary `val`s, and the input stops being the input

87 diff lines, of which **20 are new abstract operations**:

    val constant _REQUIRED_CONTRACTS : int      val ir_keys_0 () : int
    val constant _REQUIRED_FUNCTION : int       val func_keys_0 () : int
    val constant _REQUIRED_TOP : int            val contracts_keys_0 () : int
    val constant aCCEPTED_IR_VERSIONS : int     val ir_get_1 (x0: int) : int
    val contains_check (x: int) (c: int) : bool val func_get_1 (x0: int) : int
    val enumerate_1 (x0: int) : int             val func_get_2 (x0: int) (x1: int) : int
    val iter_get (x: int) (i: int) : int        val str_concat (x: int) (y: int) : int
    val iter_length (x: int) : int              val subscript_get (x: int) (i: int) : int
    ... and `pycsl_none`, `typeof_op`, `dict`, `list`

Look at `ir_keys_0 ()`. It is **nullary**: the emitted model of `ir.keys()` does not take
`ir`. Neither do `func_keys_0` or `contracts_keys_0`. The emitted program's control flow
therefore does not depend on the validator's input the way the real one does, and string
literals have become int hashes (`func_get_2 1878939832 ...`). A proof of
`#@ raises PyCSLIRError when True` + `#@ assigns \nothing` over that program says nothing
about the validator. Refused — and this is `_cache_root`'s mechanism at twenty times the
scale.

### `frontend/pure_ast.py::iter_child_nodes` — a generator whose yields are erased

Not refused by check 1 but by a plane that already exists: `bin/check-yield-erasure.py`. The
stub was converted once in an earlier generation, banked, and re-`\trusted` when the erasure
was found — the note is in the mirror file. The conversion proves `assigns \nothing` while
establishing nothing about what the generator produces, which is its entire meaning.

## The pattern, stated once

**Every check-1 refusal so far is the same shape: an operation the value model cannot carry
becomes an abstract `val` that does not take the thing it operates on.** A directory, a
dict's keys, a generator's yields. The `let` typechecks, the prover discharges it, and the
program that was verified is not the program that runs.

That is not an argument against conversion. It is the reason the screen's `--no-proof`
LOWERS verdict is a necessary condition and nothing more, and the reason the emit-diff is
check 1 rather than check 4.
