#!/usr/bin/env python3
r'''L-PLANE ORACLE: which of the compiler's ADVICE-BEARING refusals has anyone actually
followed the advice of?

WHY THIS EXISTS (#49, gen #30). `getting-better/convergence-metric-implement.md` has
carried this on its unmeasured list for generations:

    "The refusal-text surface stays unmeasured. 62 advice-bearing messages, and #90 came
     from one. No metric in the report or this plan samples English prose for
     exploitability; the advice-audit generator remains manual."

A refusal's advice is a CLAIM THE COMPILER MAKES ABOUT ITSELF, in the one place a user is
guaranteed to read, and it is the only claim in the system with no gate behind it. Route
#90 came out of one such message. Nothing since has checked another.

WHAT IT MEASURES. Every `raise PyCSL*Error(...)` in `src/pycsl/` whose message contains an
advice verb (use / rewrite / declare / add / give / call / drop / remove / replace /
instead / prefer), keyed on (file, line). 93 at the first measurement. Each AUDITED entry
records the verdict of having WRITTEN THE PROGRAM THE MESSAGE TELLS YOU TO WRITE and run
it — the only method that means anything here:

  FOLLOWABLE   the repair the message names produces a file that VERIFIES.
  UNSPELLABLE  the repair's literal text is not valid syntax.
  UNTRIED      the repair does not work; the compiler cannot do what it advises.
  AMBIGUOUS    the repair is true but under-specified — a reader who follows it the
               obvious way still gets the refusal.

THE FIRST MEASUREMENT (#49, gen #30): **198 raise sites, 94 advice-bearing, 49 AUDITED** —
24 FOLLOWABLE, 2 UNSPELLABLE, 2 UNTRIED, 1 AMBIGUOUS. 27 of 31 pieces of advice work,
which is better than I expected and is exactly why the four that do not are worth the cost
of finding. TWICE the compiler was telling users to write a program IT CANNOT COMPILE. The failures are in the three distinct ways advice can fail, and each entry
below records what was written and what happened.

FOUR MORE WERE AUDITED AND ARE NOT IN THIS POPULATION, recorded here so the work is not
lost and the number is not inflated: `Module2_Parser`'s "only .keys()/.values()/.items()
are recognised", `Module5_IREmitter`'s "only int/str/bool/None literals supported" and
"must be `Callable[[A1, ..., An], R]`", and `expressions`'s "a total=True TypedDict literal
must provide every declared key". All four are FOLLOWABLE (each was written and VERIFIES).
They state a RESTRICTION rather than an instruction, so they carry no advice VERB and this
plane's matcher does not see them. Widening the matcher to catch them takes the population
94 -> 121 and dilutes the fraction with messages that mostly say "X is unsupported"; the
narrow definition — the message TELLS YOU WHAT TO DO — is the surface route #90 came from,
so it is the one kept.

A PATTERN WORTH ITS OWN SWEEP, AND THE SWEEP'S RESULT. Two of the first 28 audits failed
the same way: the message named a `#@` directive WITHOUT ITS ARGUMENT, and a reader takes
backticked text as the thing to type. `#@ shared` and `#@ touches_field` are both syntax
errors alone. So I censused every refusal message that names an ARGUMENT-TAKING directive
in bare backticks:

    no_exception 8 · loop variant 2 · assigns 1 · depends_method 1 · requires_method 1
    footprint 1 · shared 1 · touches_field 1          (16 sites)

FOURTEEN OF THE SIXTEEN ARE DESCRIPTIVE, not instructions — "this function claims
`#@ no_exception`", "a per-index `#@ footprint` check cannot confine …", "each loop
carrying a `#@ loop variant`". Only the two already found were telling the reader to TYPE
the thing, and both are fixed. So the pattern is real and SMALL, and saying so is the
result: a census that comes back mostly innocent is worth the same as one that does not,
and it stops the next reader from re-running it. The 16 sites are the candidate list if the
distinction is ever automated.

THE RATCHET IS THE AUDITED COUNT, AND IT MAY ONLY GROW. This plane cannot check the prose
itself; what it can do is stop the manual work from evaporating. An audit that lives in a
commit message is an audit nobody can build on; an audit that lives in a baseline here is
one the next generation continues rather than repeats.

A NEW advice-bearing refusal does NOT fail this gate — it lands unaudited and the audited
FRACTION falls, which is the honest signal. What fails is the audited count going DOWN,
which means an audited message was edited (and then its verdict is stale and must be
re-derived, exactly as a message edit invalidates a refusal-witness census row).

THE POPULATION GUARD (the #44 rule): rc=2 below MIN_SITES raise sites or MIN_ADVICE
advice-bearing ones, so "everything audited" can never mean "I matched nothing".

THE SIGNATURE LENGTH IS 140 AND THAT IS MEASURED, NOT PICKED. At 64 characters, 8 keys
COLLIDED (189 distinct keys for 198 raises) — two `happy ... total target` raises in
`Module3_Weaver` share a 64-character prefix, so auditing one would have silently marked
the other audited. At 96 there are still 2 collisions; at 140 there are none. A key that
can collide turns a coverage count into an over-count, which is the failure this whole
evening has been about.

WHY THE KEY IS A TEXT SIGNATURE AND NOT A LINE NUMBER. The first version of this plane
keyed on (file, lineno) and went RED the moment an unrelated edit three functions above
shifted seven messages down a line — noise, and the kind that trains a reader to ignore a
gate. The key is now (file, the first 48 characters of the message's concatenated string
literals). That is stable under line movement and CHANGES when the message text changes,
which is exactly right: a message edit SHOULD invalidate the verdict, because the verdict
is about the words.

Usage:  bin/check-refusal-advice-audited.py [--verbose] [--list-unaudited]
'''
import argparse
import ast
import glob
import os
import re
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "pycsl")
MIN_SITES = 150
MIN_ADVICE = 70

ADVICE = re.compile(r"\b(use|rewrite|declare|add|give|call|drop|remove|replace|instead"
                    r"|prefer)\b", re.I)

FOLLOWABLE = "FOLLOWABLE"
UNSPELLABLE = "UNSPELLABLE"
UNTRIED = "UNTRIED"
AMBIGUOUS = "AMBIGUOUS"

def sig(node):
    """Stable, READABLE key for one raise: its unparsed source, normalised, first 140.

    `literal_parts` pops from a stack, so its output order is jumbled — fine for an
    ADVICE keyword match, useless as a human-checkable key. `ast.unparse` gives the
    message in source order and changes exactly when the message text changes."""
    try:
        return " ".join(ast.unparse(node).split())[:140]
    except Exception:                                   # pragma: no cover
        return "<unparse-failed>"


# (file, sig(message)) -> (verdict, what was written and what happened)
AUDITED = {
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('`for ... else` / `while ... else` is not modelled: the `else` clause runs exactly when the loop finished without `break`, a"): (FOLLOWABLE,
        "'Rewrite it with an explicit flag' — a `found` flag plus a `while` with an "
        "invariant and a variant VERIFIES."),
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('an EXTENDED slice `x[lo:hi:step]` is not modelled: the lowering is `Array.sub x lo (hi - lo)`, which ignores the step entir"): (FOLLOWABLE,
        "'Use an explicit strided loop' — works. My FIRST attempt failed on MY loop "
        "invariant, not on the advice; recorded because that distinction is the whole "
        "discipline (lesson (i3))."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' body must not `return` a value — it is a proof (returns unit). Use `pass` for an immediate arm.", c'): (FOLLOWABLE,
        "'Use `pass` for an immediate arm' — the lemma with a `pass` body VERIFIES."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' writes %s through a `nonlocal` declaration, and no certified lowering models it. `nonlocal` has no IR statement:'): (FOLLOWABLE,
        "'Return the value from the nested function instead of assigning through the "
        "closure' — VERIFIES."),
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError(f'in-place field mutation `{obj}.{field} = ...` of a record whose class `{_obj_cls}` is used as a `List[<record>]` elemen"): (FOLLOWABLE,
        "'Rebuild the record (`p = Pt(...)`) instead' — VERIFIES."),
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError('array/list with mixed or non-tuple elements alongside tuples is not supported: a faithful `array (tuple)` needs one unif"): (FOLLOWABLE,
        "'Use a uniform list of equal-arity tuples' — `[(1, 2), (3, 4)]` VERIFIES."),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot alias module global \'{node[\'value\'][\'name\']}\' into a local (inline.md Phase 3): a global is a single named objec'): (FOLLOWABLE,
        "'call its methods or read its fields directly' — VERIFIES, with a class "
        "invariant my first attempt lacked (my test, not the advice)."),

    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' writes %s through a `global` declaration, and no certified lowering models it: the store lands on a FRESH LOCAL '): (UNSPELLABLE,
        "'Declare the variable `#@ shared`' — `#@ shared` ALONE IS A SYNTAX ERROR; the "
        "grammar is `#@ shared <name>`. Spelled correctly it works, including under the "
        "DEFAULT memory model. But a `#@ shared` variable is not nameable in a contract, "
        "so `#@ assigns <name>` on the same function is then refused as undefined: you "
        "can take the advice and be unable to FRAME the write. CHECKED that this does NOT "
        "reopen route #129 — the exploit shape leaves the prover at UNKNOWN and the file "
        "FAILS. The message now gives the form and the caveat; its OTHER repair ('pass "
        "and return the value') is FOLLOWABLE."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' binds %s with a `with ... as` clause, and no certified lowering models it. `_py_stmt_with` reads only the `with`'): (UNTRIED,
        "'Call `__enter__` explicitly and assign its result' DOES NOT WORK. Two files "
        "identical except for ONE IDENTIFIER — a method returning 7 under "
        "`ensures \\result == 7`, called from a driver claiming the same — VERIFY as "
        "`enter` and FAIL as `__enter__`. `__len__` fails too and `_enter_` verifies: an "
        "explicitly-called DUNDER does not carry its contract to the call site. A "
        "COMPLETENESS gap, not an unsoundness. The message's other repair (a bare "
        "`with <lock>:`) IS followable and is now given FIRST; the broken one was "
        "withdrawn, with its measurement, so nobody re-adds it."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"function \'{name}\' is annotated `-> str` but can `return None`. Python does not enforce the hint and the model BELIEVES '): (FOLLOWABLE,
        "'Annotate `-> Optional[str]` ... or remove the `return None`' — the "
        "`Optional[str]` form VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"\'\\\\result\' is not allowed in a `#@ {node.get(\'kind\')}` in {where} (it is bound only at return; use `ensures` for return'): (FOLLOWABLE,
        "'use `ensures` for return values' — moving the claim into `#@ ensures` "
        "VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Mutable default argument in function \'{func.get(\'name\', \'<anonymous>\')}\': a list/dict/set default is a single object sh'): (UNTRIED,
        "'Use a `None` sentinel and initialise the collection in the body' DOES NOT "
        "COMPILE. `xs: Optional[List[int]] = None` emits WhyML with an UNBOUND TYPE "
        "SYMBOL `array`; isolated by controls — `List[int]` alone VERIFIES and "
        "`Optional[int]` alone VERIFIES, and only `Optional[List[T]]` fails. Three "
        "spellings of the sentinel were tried before concluding (lesson (i3)). A "
        "completeness gap in the emitter, not an unsoundness. The message now advises "
        "the form that WORKS — no default at all, the caller supplies the collection, "
        "measured — and records the broken one so nobody re-advises it."),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\' on \'{recv}\': it has a non-tail `return` (early return / return inside a branch). Verify it by '): (AMBIGUOUS,
        "'Verify it by contract' is true and under-specified. Adding a contract while "
        "KEEPING the module-global receiver does not help, and neither does "
        "`#@ \\trusted` — the inliner runs on a global-receiver call regardless. What "
        "works is a LOCAL instance (`c = C(); c.m()`), which uses the contract at the "
        "call site instead of splicing the body. The message now says so and names both "
        "things that do not work."),
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLIRError('`' + func_name + '(...)` MUTATES an ARGUMENT in place, and no certified lowering models it: the call becomes an abstract opera"): (FOLLOWABLE,
        "'Model the mutation with indexed stores' — a hand-written swap under `#@ assigns xs[0 .. 1]` VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: total target \'{hp.target}\' is marked `#@ {marker}`, so it is emitted as a bodyless `val` with no goa'): (FOLLOWABLE,
        "'give it a verified body (each loop carrying a `#@ loop variant`)' — a counting loop with an invariant and a variant VERIFIES. The SAME advice text appears on the sibling `total target reaches ...` raise; auditing it once covers both words."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: total target \'{hp.target}\' reaches \'{_r206_hit}\', which is marked `#@ \\\\trusted`, `#@ \\\\abstract` or'): (FOLLOWABLE,
        "The sibling of the entry above — same repair, same measurement."),
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError(f'aliasing a mutated dict is out of scope: `{target} = {_alias_of}` binds a SECOND NAME TO THE SAME dict in Python, and a"): (FOLLOWABLE,
        "'A read-only rebind is fine' — `e = d` with only reads through both names VERIFIES."),
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError('an `assert` whose TEST may have a SIDE EFFECT is not modelled: the test is lowered to `()`, i.e. DISCARDED, so any mutat"): (FOLLOWABLE,
        "'Move the call out of the assert and assert over the result, or give the callee `#@ assigns \\nothing`' — both halves work; the audited file binds the call to a local, gives the callee `assigns \\nothing`, and `#@ check` over the result VERIFIES."),
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLIRError('`' + func + '(...)` appends to the collection in the field `' + func.split('.')[1] + '`, and no certified lowering models it: "): (FOLLOWABLE,
        "'Rewrite it as an indexed store' — a `self.buf[i] = v` under a `\\length` class invariant and `requires 0 <= i and i < 8` VERIFIES. NOTE the standing counter-case recorded in `bin/check-stdlib-trusted-markers.py`: for `hlib.Sha256.update` the same rewrite FAILS, because that class's `__init__` can leave the field EMPTY so the `index in array bounds` sub-goal is un-dischargeable. The advice is followable when the length is pinned and not otherwise — which the message does not say."),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`ord(...)` over a NON-ASCII string is out of scope: PyCSL emits a string literal as its UTF-8 BYTES and models characters with"): (FOLLOWABLE,
        "'Use an ASCII literal' - ord of an ASCII string literal's first character VERIFIES."),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(<str>)` raises `ValueError` in Python on a non-numeric string, and this function claims `#@ no_exception` over"): (FOLLOWABLE,
        "'Drop `ValueError` from the context, or validate the string yourself' - an int() over a numeric literal with NO `#@ no_exception ValueError` VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Coroutine \'{_n.name}\' (line {_n.lineno}) carries a `#@` contract, but `async def` is NOT MODELLED: the weaver attaches '): (FOLLOWABLE,
        "'Remove the contract, or make the function synchronous' - the synchronous form VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Class \'{_hk_cls.name}\' (line {_hk_cls.lineno}) defines `{_hk_hit[0]}`, an attribute-access hook the model does not cons'): (FOLLOWABLE,
        'The repair is to remove the hook; a class with no `__getattribute__` resolves statically as the model assumes, and VERIFIES.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp_name}`: aliasing the protected base \'{vpath}\' into a local in non-exempt \'{cur_func or \'<module>\'}\' is forbi'): (FOLLOWABLE,
        "'Write through the canonical protected path, or add the method to the `except` set' - a `happy ... protects` policy whose only writer is the excepted owner, writing through the canonical path, VERIFIES."),
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"the truthiness of `{ir_expr.get(\'name\')}` is not modelled: it is bound to {_kindname}, which this lowering emits as a v'): (FOLLOWABLE,
        "'Test something the model carries instead - len(...) > 0, a membership k in ..., or an element' - the membership form VERIFIES."),
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"call to \'{func_name}\' passes {len(expr.get(\'args\', []))} positional argument(s) but parameter \'{nm}\' has no default (ar'): (FOLLOWABLE,
        'The repair is to pass every parameter that has no default; the complete call VERIFIES.'),
    ("src/pycsl/frontend/ir_resolve.py",
     'PyCSLSemanticError(f"Mixin \'{M}\' (composed into \'{C}\'): a method writes `self.{fld}`, a field declared neither `#@ shared_state` nor `#@ tou'): (UNSPELLABLE,
        "'Declare every field a mixin touches' - `#@ touches_field n` ALONE IS A SYNTAX ERROR; the form is `#@ touches_field n: <type>` and the TYPE is required. With the type it VERIFIES. The SECOND message of the audit to name an annotation without its full form, after `#@ shared` - the pattern is worth its own sweep. Message now gives the form."),
    ("src/pycsl/frontend/ir_resolve.py",
     'PyCSLSemanticError(f"Mixin composition \'{C}\': dependency \'{d[\'method\']}\' (declared by mixin \'{M}\' via #@ {d[\'kind\']}_method) has NO provider'): (FOLLOWABLE,
        "'add a mixin that `#@ provides <method>`' - a second mixin providing the dependency, composed with `#@ compose_from`, VERIFIES."),
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError("`del <seq>[i:j]` (a SLICE delete) is not modelled: Python\'s slice `del` REMOVES a whole range, shifting every later elem'): (FOLLOWABLE,
        "'Rewrite the deletion as an explicit shift loop, or delete the elements one at a time' - an indexed loop with an invariant and a variant VERIFIES."),
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError("`del <obj>.<attr>` (an ATTRIBUTE delete) is not modelled: it was lowered to a bare no-op, so the model KEEPS the deleted'): (FOLLOWABLE,
        "'model the reset explicitly with an assignment' - a `self.n = 0` method under `#@ assigns self.n` VERIFIES."),
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('`try ... except*` (an exception-GROUP handler) is not modelled: `_PY_STMT_HANDLERS` has no `TryStar` entry and `_py_stmts_t"): (FOLLOWABLE,
        "'Rewrite with a plain `except`' - the plain handler VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"""`#@ \\\\diverges` on function \'{func.get(\'name\', \'<anonymous>\')}\' is not justified: its body has no potentially-divergi'): (FOLLOWABLE,
        "'Remove `#@ \\\\diverges`, or give the body a construct that can actually block or loop' - a `while` loop under `#@ \\\\diverges` VERIFIES. My first attempt failed on a missing loop invariant (my test, not the advice)."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`-> NoReturn` on function \'{name}\' is not justified: its body has no `raise` and no potentially-diverging construct (no'): (FOLLOWABLE,
        "'Remove `-> NoReturn`, or give the body a raise/divergence' - a body that raises VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Dead code in function \'{fname}\': this statement follows a call to a `NoReturn` function, which never returns normally ('): (FOLLOWABLE,
        "'Remove the dead statement, or move it before the NoReturn call' - a call to a NoReturn function with no dead code after it VERIFIES. TWO attempts failed first, both on MY file: the caller must declare the exception, and the clause form is `#@ raises E when <cond>` - `#@ raises E` alone is a syntax error, a THIRD bare-directive case."),
    ("src/pycsl/frontend/module5/memoization_rt.py",
     'PyCSLIRError(f"Function \'{f[\'name\']}\': a memoizing decorator (lru_cache / cache / cached_property) requires a referentially transparent func'): (FOLLOWABLE,
        "'Read only fields written by the constructor, or drop the decorator' - an `@lru_cache` method reading a constructor-only field VERIFIES."),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r71_f + '(...)` can raise `KeyError` in Python, and this function claims `#@ no_exception` over it — but the mutation of"): (FOLLOWABLE,
        "'Return the updated collection instead, or drop the parameter from the contract' - dropping the mutated parameter from the contract VERIFIES."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLSemanticError(f"storing a mutated dict into a field is out of scope: `{_s.get(\'object\')}.{_s.get(\'field\')} = {_pname}` binds the field '): (FOLLOWABLE,
        "'A field store whose local is never used again is fine' - `self.d = src` with no later use of `src` VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' has no `#@ ensures`: a lemma must state the fact it proves (the conclusion). Add at least one `#@ e'): (FOLLOWABLE,
        "'a lemma must state the fact it proves' - a lemma carrying an `#@ ensures` VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' is also `#@ \\\\diverges`: a non-terminating lemma proves nothing and would be unsound as a fact. Rem'): (FOLLOWABLE,
        'The repair is to drop `#@ \\\\diverges` from the lemma - the plain lemma VERIFIES.'),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Invalid use of \'\\\\result\' in {ctx}. It is only allowed in \'ensures\'.", code=\'PYCSL-SEM-RESULT\')'): (FOLLOWABLE,
        "'It is only allowed in ensures' - moving the `\\\\result` claim into `#@ ensures` VERIFIES."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Subscript assignment to immutable \'bytes\' variable \'{arr.get(\'name\')}\' in {where} — a Python `bytes` object does not su'): (FOLLOWABLE,
        'The repair is a `bytearray` - `b = bytearray(2); b[0] = 7` VERIFIES. NOTE the standing route #214 note: `bytes(n)` is left ILL-TYPED on purpose (witness 1725), so the refusal and the type error are doing different halves of the same job.'),
    ("src/pycsl/frontend/Module1_Ingestor.py",
     "PyCSLParseError('tabs are not allowed in `act` block indentation; use 4 spaces', stage='Module1')"): (FOLLOWABLE,
        "'use 4 spaces' - a four-space-indented `act` block VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Class \'{node.name}\' (line {node.lineno}): `__del__` finalizer is rejected under UB-7.5. Finalizer timing is non-determi'): (FOLLOWABLE,
        'The repair is to remove the finalizer - the same class without `__del__` VERIFIES.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     "PyCSLSemanticError('a function, method or class NAME is rebound after its definition (' + '; '.join(sorted(set(_rb_bad))) + '). Every call i"): (FOLLOWABLE,
        "'Give each binding its own name' - two distinctly-named functions VERIFY."),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"\\\\length is not supported on the {typ}-typed \'{var}\' in {ctx}: dicts/sets are modelled as total maps (`map int (option '): (FOLLOWABLE,
        "The repair the message names ('dicts/sets are modelled as total maps ... use a membership') - a `1 in d` precondition VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: trusted/abstract function \'{fn.name}\' is not exempt and has no checkable body, so it could write the'): (FOLLOWABLE,
        'Both repairs work: adding the trusted writer to the `except` set VERIFIES, and so does giving it `#@ \\\\preserves`.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: trusted/abstract method \'{fn.name}\' is not exempt and its `assigns` writes a protected path ({\', \'.j'): (FOLLOWABLE,
        'Same pair of repairs as the function-level sibling, measured the same way: `except` and `#@ \\\\preserves` both VERIFY.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}({hp.param})`: non-exempt \'{fn.name}\' performs a {kind} store to the protected path \'{path}\' (line {get'): (FOLLOWABLE,
        "'Write through <path>[i] one index at a time so each write is confined' - a per-index store under `#@ footprint <policy>(k)` VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: non-exempt \'{fn.name}\' REBINDS the whole field \'self.{hp.field}\' (line {getattr(nd, \'lineno\', 0)}), '): (FOLLOWABLE,
        'The repair is to write THROUGH the protected field rather than rebind it; an indexed store by the excepted owner VERIFIES.'),
}


def literal_parts(node):
    out, stack = [], [node]
    while stack:
        n = stack.pop()
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.append(n.value)
        elif isinstance(n, ast.JoinedStr):
            stack.extend(n.values)
        elif isinstance(n, ast.BinOp):
            stack.extend([n.left, n.right])
        elif isinstance(n, ast.Call):
            stack.extend(n.args)
    return out


def sites():
    raises, advice = 0, []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for f in sorted(glob.glob(os.path.join(SRC, "**", "*.py"), recursive=True)):
            try:
                tree = ast.parse(open(f, errors="replace").read())
            except SyntaxError:
                continue
            for n in ast.walk(tree):
                if not isinstance(n, ast.Raise) or not isinstance(n.exc, ast.Call):
                    continue
                nm = getattr(n.exc.func, "id", None) or getattr(n.exc.func, "attr", None)
                if not nm or not str(nm).startswith("PyCSL"):
                    continue
                raises += 1
                msg = " ".join(literal_parts(n.exc))
                if ADVICE.search(msg):
                    advice.append((os.path.relpath(f, ROOT), n.lineno, msg[:90],
                                   sig(n.exc)))
    return raises, advice


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--list-unaudited", action="store_true")
    args = ap.parse_args()

    raises, advice = sites()
    if raises < MIN_SITES:
        print("[!] refusal-advice-audited: REFUSING — only %d raise site(s) found, "
              "expected at least %d. The walk is broken; this is not a pass."
              % (raises, MIN_SITES), file=sys.stderr)
        return 2
    if len(advice) < MIN_ADVICE:
        print("[!] refusal-advice-audited: REFUSING — only %d advice-bearing message(s) "
              "matched, expected at least %d. The matcher is broken; this is not a pass."
              % (len(advice), MIN_ADVICE), file=sys.stderr)
        return 2

    keys = {(f, sg) for f, _ln, _m, sg in advice}
    line_of = {(f, sg): ln for f, ln, _m, sg in advice}
    done = sorted(k for k in keys if k in AUDITED)
    todo = sorted(k for k in keys if k not in AUDITED)
    stale = sorted(k for k in AUDITED if k not in keys)
    by = {}
    for k in done:
        by[AUDITED[k][0]] = by.get(AUDITED[k][0], 0) + 1

    print("[*] refusal-advice-audited: %d raise site(s), %d carry ADVICE; %d audited "
          "(%s), %d not."
          % (raises, len(advice), len(done),
             ", ".join("%s %d" % (k, v) for k, v in sorted(by.items())) or "none",
             len(todo)))

    if args.verbose or args.list_unaudited:
        for f, ln, m, sg in sorted(advice):
            if (f, sg) in AUDITED:
                if args.verbose:
                    print("    %-12s %s:%d" % (AUDITED[(f, sg)][0], f, ln))
            else:
                print("    unaudited    %s:%d  %s" % (f, ln, m[:60]))

    rc = 0
    for f, sg in stale:
        print("[!]   AUDITED ENTRY %s / %r NO LONGER MATCHES an advice-bearing raise. The "
              "message moved or was edited, so its verdict is STALE — re-run the audit "
              "and update the entry, exactly as a message edit invalidates a "
              "refusal-witness census row." % (f, sg), file=sys.stderr)
        rc = 1
    if len(done) < MIN_AUDITED:
        print("[!]   AUDITED COUNT FELL: %d < %d. This may only grow." % (len(done),
              MIN_AUDITED), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] refusal-advice-audited: NOT OK.", file=sys.stderr)
    else:
        print("[+] refusal-advice-audited: OK — %d of %d advice-bearing refusal(s) have "
              "had their advice FOLLOWED and run (floor %d). The rest are unaudited, "
              "which is a debt this plane exists to make visible rather than a failure."
              % (len(done), len(advice), MIN_AUDITED))
    return rc


MIN_AUDITED = 49

if __name__ == "__main__":
    sys.exit(main())
