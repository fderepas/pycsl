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

## The fourth clause of check 1, found at the boundary: the conversion must MOVE a claim

`frontend/Module5_IREmitter.py::PyCSLToJSONEmitter._array_init_size` PROVES. Its emit-diff is
76 lines and introduces **twenty-two** new abstract operations — and every single one takes
its operand, so the three clauses stated so far all admit it:

    val get_BinOp (x) · get_List (x) · get_Mult (x) · get_args (x) · get_elts (x) ·
    get_func (x) · get_id (x) · get_left (x) · get_op (x) · get_right (x) ·
    iter_get (x) (i) · iter_length (x) · subscript_get (x) (i) ·
    py_isinstance_BinOp_int_op (x) · _Call_ · _Constant_ · _List_ · _Mult_ · _Name_ ·
    _bytes_int_op (x) · pyCSLToJSONEmitter__const_int_value_1 (x0)

**Every operation in the body is an oracle.** The function walks an AST to compute a size; the
model sees an unconstrained int produced by unconstrained accessors from an unconstrained
input.

And its contract is

    #@ requires True    #@ ensures True    #@ assigns \nothing
    @staticmethod
    def _array_init_size(rhs: ast.expr) -> int:

A `@staticmethod`. There is no `self`, so `assigns \nothing` has no field frame to prove.
`ensures True` claims nothing. **So the conversion moves NO clause from assumed to proved.**

That is the campaign's own sentence, applied:

> `\trusted` is not a hole in the proof; it is a LABEL on a claim nobody checked, and removing
> the label re-files the claim from ASSUMED to PROVED — **an improvement only if the model can
> SEE the thing the claim is about.**

Here the model can see nothing the claim is about, and there is no claim. So:

### CHECK 1, CLAUSE 4 — a conversion must MOVE A CLAUSE from ASSUMED to PROVED

Not "must prove". Not "must introduce no `val`s". **Must move something.** Concretely, the
emit-diff must show at least one of:

* a `requires` / `ensures` / `raises` / frame clause that the `val` ASSUMED and the `let`
  DISCHARGES — `errors.py::message` moves four frame `ensures`, times four inheriting classes;
  `Module2_Parser::_err` moves `ensures { false }`, which becomes a proof that it never returns
  normally;
* or a body whose operations are MODELLED, so the `let` says something the `val` could not —
  `Module6_WhyMLTranspiler::__init__` moves 172 lines of field initialisation into the record
  model and adds twelve fields the model did not know existed.

`_array_init_size` does neither. It is a `val` rewritten as a `let` over the same opacity, and
retiring its marker would move the count without moving the model — which is the exact defect
`bin/check-untrusted-emitted.py` was built to catch, in the one form that plane cannot see
(the function IS emitted as a `let`; it just doesn't say anything).

**REFUSED.** Not landed.
