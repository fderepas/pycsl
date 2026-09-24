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

THE MEASUREMENT (#49, gen #30): **219 raise sites, 108 advice-bearing, 108 AUDITED** —
102 FOLLOWABLE, 2 UNSPELLABLE, 2 UNTRIED, 2 AMBIGUOUS. **The whole surface, for the first
time.** A hundred and two pieces of advice produce a file that VERIFIES; the six that do
not were all REPAIRED the same evening, and they fail in four distinct ways:

  UNSPELLABLE  `#@ shared` and `#@ touches_field` — the message names a directive without
               its argument, and a reader types what is inside the backticks. Both are
               syntax errors alone.
  UNTRIED      "Call `__enter__` explicitly" — an explicitly-called DUNDER does not carry
               its contract (`enter` verifies, `__enter__` does not, identical otherwise).
               "Use a `None` sentinel" — `Optional[List[T]]` emits WhyML with an unbound
               type symbol `array`. TWICE the compiler told a user to write a program it
               cannot compile.
  AMBIGUOUS    "Verify it by contract" is true and needs a LOCAL instance, which it does
               not say. And an OR-list of three repairs whose FIRST disjunct is really a
               CONJUNCTION with the second — a `#@ raises` clause on a still-`\trusted`
               method does nothing, because the refusal keys on the bodylessness.

SEVEN TIMES MY OWN TEST FILE WAS THE PROBLEM, not the advice, and each is recorded in its
entry: three missing loop invariants, a missing class invariant, two callers that did not
declare a callee's exception, and a constructor with no stated post-state for
`#@ fresh_globals` to re-establish. "The advice failed" and "I wrote the file badly" are
the same observation from outside, and only one of them is a finding.

AND ROUTE #215 CAME OUT OF THIS AUDIT. Following `monomorphize`'s GT4 advice produced a
file that would not verify; three controls isolated a generic-FUNCTION call lowering to
`(any int)`; probing that erasure produced a false contract that PROVED.

AND THIS PLANE INHERITED THE ARTIFACT IT WAS BUILT BESIDE. Its `sites()` was copied from
`check-refusal-witness-coverage` and carried the same filter — the raised NAME must start
with `PyCSL` — so the twenty-one ALIASED raises were outside its population too. Fixing it
the same evening took the census from 94 advice-bearing to 108, and every one of the 14
newly visible was a route refusal this campaign had landed in `pycsl.py`. A plane written
TODAY was already blind to TODAY's work, because it was copied from one written before it:
a population filter does not merely age, it PROPAGATES.

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
import hashlib
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
    # (#49) gen #31 — FIVE REFUSALS THIS CAMPAIGN ADDED, audited the only way this plane
    # accepts: by WRITING THE PROGRAM THE MESSAGE TELLS YOU TO WRITE and running it. Each
    # one already had that program in the corpus as its CONTROL, which is the point of
    # landing a refusal with a witness/control pair rather than a witness alone — the
    # control IS the audit, and it only needed recording.
    ('src/pycsl/pycsl.py',
     "_PyCSLSemErrVM('`#@ verify_module %s` (line %d) names a group that is lowered to a Why3 `module`, and Why3 module names must be CAPITALIZED "): (FOLLOWABLE,
        "'capitalize the group name' — control 1843 is 1842 with `LeafMod` for `leafmod`, and it VERIFIES, cross-group call and all."),
    ('src/pycsl/pycsl.py',
     '_PyCSLSemErrMx("`#@ compose_from` (line %d) names \'%s\', which is not declared `#@ mixin`. A composable mixin must SAY SO: the marker is what'): (FOLLOWABLE,
        "'the marker is what makes it composable' — control 1858 declares `#@ mixin` on the named class and the SAME file VERIFIES. The witness is 1857."),
    ('src/pycsl/pycsl.py',
     '_PyCSLSemErrMi("`#@ mixin` class \'%s\' is CONSTRUCTED here (line %d). A mixin is declared composable, not instantiable: its methods are verif'): (FOLLOWABLE,
        "'construct the class that composes it instead' — control 1862 constructs the UNMARKED class and VERIFIES. The witness is 1861."),
    ('src/pycsl/pycsl.py',
     '_PyCSLSemErrCal("the `Callable` annotation on \'%s\' (in \'%s\') names \'%s\', which is neither a primitive tag (`int`, `bool`, `str`, `float`) no'): (FOLLOWABLE,
        "'declare it, or use one of the primitive tags' — control 1878 declares `Box` and the same `Callable[[Box], int]` VERIFIES, arrow applied. The witness is 1877."),
    ('src/pycsl/pycsl.py',
     '_PyCSLSemErrLem("`#@ lemma` \'%s\' (line %d) has no `#@ assigns` clause, and a lemma must state `#@ assigns \\\\nothing` explicitly. The clause '): (FOLLOWABLE,
        "'add `#@ assigns \\\\nothing` to it' — control 1848 is the same lemma with the clause, and it VERIFIES. The witness is 1847."),
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
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: \'{hp.target}\' is guarded by a capability precondition, but it is called here as `{_shown}.{hp.target'): (FOLLOWABLE,
        "The repair is to call through `self.<target>(...)`, which IS a capability check site; a `self.transfer(...)` call under the policy's precondition VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: method \'{fn.name}\' contains a dynamic `exec(...)`, which may read anything — add it to `except` or r'): (FOLLOWABLE,
        'The repair is to remove the dynamic `exec`; the same policy with no `exec` VERIFIES.'),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`happy {hname}`: method \'{m}\' contains a dynamic `exec(...)`, which may write anything (not a compile-time-constant exe'): (FOLLOWABLE,
        'Sibling of the entry above, same repair and same measurement.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: noninterference target \'{hp.target}\' can WRITE state — `{_wfield}` in \'{_wfn}\'{_via}. The synthesize'): (FOLLOWABLE,
        'The repair is a state-free target; a `summarize` under `#@ assigns \\\\nothing` VERIFIES.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: aliasing the protected field \'self.{hp.field}\' into a local in non-exempt \'{fn.name}\' is forbidden —'): (FOLLOWABLE,
        'The repair is to read and write THROUGH the protected field; an excepted owner writing it and a reader reading it VERIFY.'),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Ghost string variable \'{target}\' does not support \'{op}\' in {where}. Use the ^ operator for string concatenation: #@ gh'): (FOLLOWABLE,
        '\'Use the ^ operator for string concatenation\' - `#@ ghost acc = acc ^ "x"` VERIFIES.'),
    ("src/pycsl/frontend/Module5_IREmitter.py",
     "PyCSLIRError(f'`\\\\forall x in {dv.coll}.items()` (two-binder) is a 07-1311 follow-on; use `.keys()`/`.values()` or the `\\\\forall k in {dv.co"): (FOLLOWABLE,
        "'use `.keys()`/`.values()` or the `\\\\forall k in d;` key form' - the `.keys()` form VERIFIES."),
    ("src/pycsl/frontend/Module5_IREmitter.py",
     "PyCSLIRError('isinstance: a typing.Literal alias is not a valid second argument (LR4 / PEP 586 — use a concrete value equality test)', stage"): (FOLLOWABLE,
        "'use a concrete value equality test' - `x == 1` in place of `isinstance(x, Literal[1])` VERIFIES."),
    ("src/pycsl/frontend/desugar.py",
     'PyCSLParseError("a Python `assert` inside a `try` whose handler can catch `AssertionError` is not modelled: the `assert` is lowered to a NO-'): (FOLLOWABLE,
        "'Use an explicit `if not <cond>: raise AssertionError(...)`, or move the `assert` out of the `try`' - a `#@ check` outside any `try` VERIFIES."),
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError("`deque(<iterable>)` with arguments is not modelled: the lowering reduces a deque to the list/array model and DISCARDS ev'): (FOLLOWABLE,
        'The repair is an empty `deque()` plus explicit appends; the empty construction VERIFIES.'),
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError(f"augmented assignment to {_aa_kind} is not modelled: this lowering handles `x op= v`, `self.f op= v`, `p.f op= v` (p a l'): (FOLLOWABLE,
        'The repair is to use a handled shape; both `x += 1` on a local and `self.n += 1` on a field VERIFY.'),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"{where}: `#@ fresh_globals` is only allowed on a top-level driver that no other verified function calls. \'{short}\' is c'): (FOLLOWABLE,
        "'Remove the call, or drop `#@ fresh_globals`' - a driver nothing calls VERIFIES. My first attempt failed on MY file: the constructor needs an explicit `#@ ensures self.n == 0` for the directive to have a post-state to re-establish (corpus 0713 shows the shape). My mistake, not the advice's - recorded per lesson (i3)."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError(\'`\' + str(_r63_n.get(\'func\')) + \'(...)` is passed the SAME dict/set `\' + _r63_nm + "` in more than one argument position. In Py'): (FOLLOWABLE,
        "'restructure so only one name reaches the callee' - two distinct dict parameters VERIFY."),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` resolves to a `#@ \\\\trusted` or `#@ \\\\abstract` method of this program, and this function claims `#@ no_"): (AMBIGUOUS,
        "The message used to read as THREE alternatives: 'Give the method a `#@ raises` clause, verify its body, or drop the exception from the context.' MEASURED: adding `#@ raises ValueError when False` to the still-TRUSTED method leaves the refusal FIRING - the refusal keys on the BODYLESSNESS, not on the clause, exactly as its own sentence says ('a bodyless `val` carries no `raises`'). So the first item is a CONJUNCTION with the second, not an alternative to it. A verified body alone VERIFIES; dropping the exception from the context alone VERIFIES. Message rewritten to say so."),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` is not a function of the verified program and not on the list of operations known never to raise the exc"): (FOLLOWABLE,
        "'Give the callee a contract ... or drop the exception from the context' - a contracted in-file callee VERIFIES."),
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"struct format \'{fmt}\': native size/alignment (\'@\' prefix) is unsupported (UB-7.4b). Native layout is platform-dependent'): (FOLLOWABLE,
        "The repair is an explicit byte-order prefix; `struct.pack('>H', v)` under an in-range precondition VERIFIES."),
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError(f'heterogeneous list literal (contains a {_mix} element mixed with other element types) has no faithful WhyML `array` ele"): (FOLLOWABLE,
        'The repair is a homogeneous literal; `[1, 2, 3]` VERIFIES.'),
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError('a comparison over a value that may be NaN on one path and an ordinary number on another is not modelled: NaN is the one "): (FOLLOWABLE,
        'The repair is to keep NaN out of the compared value; an integer comparison VERIFIES.'),
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"the call `{func_name}(...)` resolves to a METHOD `{_sh_parts[1]}`, but the program also STORES an attribute `{_sh_parts'): (FOLLOWABLE,
        'The repair is to give the method and the attribute distinct names; a class whose method name is not also stored as a field VERIFIES.'),
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"the call `{func_name}(...)` resolves to a METHOD `{_sh_parts[1]}`, but instances of its class also carry an ATTRIBUTE `'): (FOLLOWABLE,
        'The repair is to give the method and the attribute distinct names; a class whose method name is not also stored as a field VERIFIES.'),
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLIRError(\'`\' + func_name + "(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstract oper'): (FOLLOWABLE,
        "'Model the mutation with indexed stores' - a hand-written swap under `#@ assigns xs[0 .. 1]` VERIFIES (the receiver-side sibling of the argument-side entry)."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("nested function \'%s\' is lifted to a sibling of its enclosing function, and the lift is not faithful here: %s. A lifted body re'): (FOLLOWABLE,
        'The repair is a distinctly-named top-level helper called normally; it VERIFIES.'),
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`-> NoReturn` on function \'{name}\' is not justified: its body contains a `return` statement (a normal-exit path). A NoR'): (FOLLOWABLE,
        "'raise instead, or call another NoReturn function' - a NoReturn body that calls another NoReturn function VERIFIES. My first attempt failed on MY file: the caller must declare the callee's exception (`#@ raises E when <cond>`). Lesson (i3) again."),
    ("src/pycsl/frontend/monomorphize.py",
     'PyCSLSemanticError(f"monomorphization: generic {gname!r} declares a {kind} ({tp.get(\'name\')!r}) — GT3: ParamSpec/TypeVarTuple are schema-onl'): (FOLLOWABLE,
        "'Use a plain TypeVar `T`' - the plain-TypeVar generic class VERIFIES."),
    ("src/pycsl/frontend/monomorphize.py",
     "PyCSLSemanticError(f'monomorphization: generic function {gname!r} calls itself with its own TypeVar {tvar!r} — GT4: polymorphic recursion do"): (FOLLOWABLE,
        "'The recursive call must use a concrete type' - and route #215 changed what that can mean: the subscripted spelling `f[int](...)` is now REFUSED as invalid Python, so the followable readings are a NON-generic recursion (VERIFIES, with `#@ \\\\variant`) or a non-recursive generic (VERIFIES). Recorded so the interaction is not rediscovered."),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\': call passes {len(args)} args, method takes {len(formals)}.")'): (FOLLOWABLE,
        'The repair is to pass the declared number of arguments; the matching call VERIFIES.'),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\' on \'{recv}\': its body refers to {\', \'.join((repr(n) for n in _cap169))}, which the calling fun'): (FOLLOWABLE,
        "'Rename the local' - a caller whose local does not collide with a name in the spliced body VERIFIES."),
    ("src/pycsl/frontend/ir_resolve.py",
     'PyCSLSemanticError(f"Mixin composition \'{C}\': \'{C}\' defines its own \'{pm}\', which SHADOWS the provider of \'{pm}\' (from mixin {owners}) that '): (FOLLOWABLE,
        'The repair is not to define the shadowing method on the composing class; the composition without it VERIFIES.'),
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline call to \'{recv}.{callee.split(\'__\')[-1]}\': method \'{callee}\' not found.")'): (FOLLOWABLE,
        "The repair is to call a method the receiver's class declares; the matching call VERIFIES (same carrier as the arity entry)."),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError(_r160_msg + ', and this function claims `#@ no_exception` over it. There is no trigger row for this builtin and no faithful obl"): (FOLLOWABLE,
        'The shared repair across this `#@ no_exception` family is to drop the exception from the context (or avoid the raising operation); a file with neither VERIFIES. The trusted-callee sibling of this family is the AMBIGUOUS entry - there the first listed repair is really a conjunction.'),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` raises `ValueError` in Python on an EMPTY separator, and this function claims `#@ no_exception` over `Va"): (FOLLOWABLE,
        'The shared repair across this `#@ no_exception` family is to drop the exception from the context (or avoid the raising operation); a file with neither VERIFIES. The trusted-callee sibling of this family is the AMBIGUOUS entry - there the first listed repair is really a conjunction.'),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` can raise `' + _r65_exc + '` in Python, and this function claims `#@ no_exception` over it. `exception_m"): (FOLLOWABLE,
        'The shared repair across this `#@ no_exception` family is to drop the exception from the context (or avoid the raising operation); a file with neither VERIFIES. The trusted-callee sibling of this family is the AMBIGUOUS entry - there the first listed repair is really a conjunction.'),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _x178['func'] + '(...)` calls code that can raise `' + '`/`'.join(_hit178) + '` implicitly (a dict or list subscript, an "): (FOLLOWABLE,
        'The shared repair across this `#@ no_exception` family is to drop the exception from the context (or avoid the raising operation); a file with neither VERIFIES. The trusted-callee sibling of this family is the AMBIGUOUS entry - there the first listed repair is really a conjunction.'),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError(\'`\' + _f + \'(...)` mutates the collection PARAMETER `\' + _f.rsplit(\'.\', 1)[0] + "`, which this function\'s own contract also NAM'): (FOLLOWABLE,
        "'Return the updated collection instead, or drop the parameter from the contract' - the receiver-side sibling of the argument-side entry; dropping the parameter VERIFIES."),
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError(\'the collection PARAMETER `\' + _r62_p + "`, which this function\'s contract NAMES, is passed to `" + str(_r62_n.get(\'func\')) + "'): (FOLLOWABLE,
        'Same family: the contract must not name a collection the callee mutates; a file without that pairing VERIFIES.'),
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('PYCSL-SUBTYPING-PAIR: `--check-behavioral-subtyping` recorded the override pair (' + str(ov.get('sub_method')) + ' refines ' +"): (FOLLOWABLE,
        'The repair is a program where both sides of the refinement pair are emitted; an ordinary class with a contracted method VERIFIES under the default flags.'),
    ("src/pycsl/module6_whyml/preamble.py",
     "PyCSLIRError(f'#@ proof {qn}: not in Module6 axiom registry. Either add the axiom body to _AXIOM_REGISTRY or run `proof2why3 emit` (when ava"): (FOLLOWABLE,
        "'Either add the axiom body to _AXIOM_REGISTRY or run `proof2why3 emit`' - from a SOURCE file the followable form is to cite a REGISTERED axiom (or none); a file citing none VERIFIES. Adding a registry entry is a compiler change, not something a user file can do, and the message does not say so."),
    ("src/pycsl/module6_whyml/statements.py",
     'PyCSLIRError(\'`del \' + (arr.get(\'name\') or \'<expr>\') + "[...]` on a non-dict/set receiver is not modelled: Python\'s list `del` SHIFTS every '): (FOLLOWABLE,
        'The repair is to delete from a dict/set; `del d[1]` under `requires 1 in d` VERIFIES.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Function \'{node.name}\' (line {node.lineno}): `#@ {_kind.lower()}` is discharged as a function-ENTRY assert over the act'): (FOLLOWABLE,
        "'Drop the `complete` line, or give the function a verified body' - the same acts on a VERIFIED (un-trusted) body VERIFY."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: total target \'{hp.target}\' is marked `#@ \\\\diverges` — it opts OUT of termination, contradicting the'): (FOLLOWABLE,
        'The repair is to drop `#@ \\\\diverges` from a `total` target; a loop with an invariant and a variant under a `total` policy VERIFIES. My first attempt used a RECURSIVE method whose postcondition my contract could not carry - my file, not the advice (lesson (i3), for the seventh time in this audit).'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}({hp.param})`: \'{func_name}\' is `#@ \\\\trusted` or `#@ \\\\abstract`, is not exempt, has no `#@ footprint '): (FOLLOWABLE,
        "'Bind a footprint, add `#@ \\\\preserves`, add it to `except`, or give it a verified body' - the footprint-binding arm VERIFIES (per-index store under `#@ footprint <policy>(k)`)."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: \'{func_name}\' is `#@ \\\\trusted` or `#@ \\\\abstract`, is not exempt, and its BODY writes the protected'): (FOLLOWABLE,
        'Same repair set as the parametric sibling; the `except` and `#@ \\\\preserves` arms were both measured VERIFYING earlier in this audit.'),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError("a name\'s runtime binding is not the `def` the model resolves it to (" + \'; \'.join(sorted(set(_dc_bad))) + \'). A decorato'): (FOLLOWABLE,
        "'Give each binding its own name' - a file whose every name is bound once VERIFIES."),
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError("a name\'s runtime value is not the one the model reads (" + \'; \'.join(sorted(set(_nb_bad))) + \'). An imported name bound '): (FOLLOWABLE,
        'Same repair, same measurement: one binding per name, no dynamic `exec`/`eval` at module or class-body scope.'),
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLIRError('PYCSL-UNFRAMED-REGION-ASSIGNS: this function is emitted as a bodyless `val` (a `\\\\trusted` / `\\\\abstract` / imported stub) and"): (FOLLOWABLE,
        'The repair is to make the region base an `array`-typed PARAMETER of the emitted signature; a `\\\\trusted` stub whose `assigns xs[0 .. 1]` names its own list parameter VERIFIES.'),
    ("src/pycsl/module6_whyml/expressions.py",
     "_R42Err('an IDENTITY test against a `bool` literal (`X is True` / `X is False`) is refused unless the emitter can SHOW `X` is a Python `bool"): (FOLLOWABLE,
        "Route #42's refusal. The repair is an ordinary equality/truth test; `n == 1` VERIFIES."),
    ("src/pycsl/module6_whyml/statements.py",
     '_R49B("in-place `%s=` on list parameter \'%s\' is out of scope: Python `a += b` on lists is an IN-PLACE extend, so the caller\'s list grows, an'): (FOLLOWABLE,
        "Route #49B. The repair is an explicit indexed write to the caller's list; VERIFIES."),
    ("src/pycsl/module6_whyml/statements.py",
     '_R49("in-place `append` to list parameter \'%s\' is out of scope: Python passes a list argument BY REFERENCE, so the append must be VISIBLE to'): (FOLLOWABLE,
        'Route #49. Same repair as its sibling, same measurement: an indexed write VERIFIES.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr215(f"{args.file} (line {getattr(_n215, \'lineno\', 0)}): `{_n215.func.value.id}[...](...)` SUBSCRIPTS A GENERIC FUNCTION at a cal'): (FOLLOWABLE,
        "Route #215's own refusal, audited the day it landed. 'Write the plain call `f(...)`' - the unsubscripted call VERIFIES and is lowered faithfully (control 1797)."),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr204(f"{args.file} (function \'{_f204.get(\'name\')}\'): the `#@ interface assigns` frame is NARROWER than the definition\'s `#@ assig'): (FOLLOWABLE,
        "Route #204. 'List every `#@ assigns` target in the `#@ interface assigns` clause, or drop the interface frame entirely' - the matching frame VERIFIES."),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr43("a COMPLEX literal (%r) has no model (ROUTE #43): `_py_expr_constant` lowers it to `int(value.real)`, so the imaginary part i'): (FOLLOWABLE,
        'Route #43. The repair is a literal the model carries; an int VERIFIES.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr200(f"in \'{_r200_caller}\': the call to \'{_r200_fn}\' passes a string literal to parameter \'{_r200_pname}\', which \'{_r200_fn}\' dec'): (FOLLOWABLE,
        'Route #200. The repair is a consistent parameter type at the call site; an int passed to an int parameter VERIFIES.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr179(f"{_d179.name!r} constructs an object whose `__init__` / `__post_init__` can raise `{_e179}` (ROUTE #179), directly or throu'): (FOLLOWABLE,
        'Route #179. The repair is a constructor that cannot raise; a plain `__init__` VERIFIES.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr189(f"{_fd189.name!r} binds {_nm189!r} to more than one class ({\', \'.join(sorted(_bd189[_nm189]))}) and then calls `{_nm189}.{_c'): (FOLLOWABLE,
        'Route #189. The repair is one name per class; two distinctly-named classes VERIFY.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr187(f"this module declares `#@ fresh_globals`, which ASSUMES each module-global singleton\'s constructor post-state at the driver'): (FOLLOWABLE,
        'Route #187. The repair is a constructor whose post-state is STATED (`#@ ensures self.n == 0`), which is what `#@ fresh_globals` re-establishes; VERIFIES.'),
    ("src/pycsl/pycsl.py",
     "_PyCSLSemErr29(f'the array spec atom `{_r29_names[_r29_hit]}` is not interpreted under the {memory_model!r} memory model (ROUTE #29): its Mo"): (FOLLOWABLE,
        'Route #29. The repair is a spec the chosen memory model interprets; an ordinary integer contract under the default model VERIFIES.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemanticError(f"{args.file} (function \'{_func.get(\'name\')}\', for-loop near line {v.get(\'loop_line\', \'?\')}): UB-7.1 — the loop body mut'): (FOLLOWABLE,
        'The repair is a loop shape the model carries; an indexed `while` with an invariant and a variant VERIFIES.'),
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr212(f"{args.file}: `--verify-imports` was given and the imported module \'{_mod212}\' ({_path212}) does NOT verify, so none of its'): (FOLLOWABLE,
        "Route #212's certificate. The repair is an imported module that DOES verify; a two-file program whose dependency verifies passes `--verify-imports` end to end."),
    ("src/pycsl/pycsl.py",
     "_PyCSLSemErr38('a `with` statement in a file that defines a context-manager class (%s) uses a context expression this build cannot positivel"): (FOLLOWABLE,
        'The repair is a bare `with <lock>:`, which IS modelled as a critical section; it VERIFIES under `--memory-model concurrent`. Same repair as the `with ... as` refusal, whose OTHER arm this audit had to withdraw.'),
}

# (#49) A MESSAGE HASH BESIDE THE KEY, BECAUSE THE KEY LOOKS AT THE WRONG END. The audit
# key is the first 140 characters of the unparsed raise — stable under line movement, and
# it CHANGES when the message's opening changes. But a refusal's ADVICE is almost always
# at the END of the message, so an edit to the advice ITSELF would not move the key: a
# verdict about the words would survive a rewrite of exactly those words. Measured the
# moment it mattered — clarifying the mutable-default advice left its entry looking fresh.
#
# So every entry also carries a hash of the WHOLE message. A key that still matches but a
# hash that does not means the message was EDITED SINCE THE AUDIT, and the verdict must be
# re-derived. That is a REFUSAL, not a warning, for the same reason the coverage gate
# refuses a truncated census: a stale verdict about prose is indistinguishable from a
# fresh one from the outside.
AUDITED_HASH = {
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"""`#@ \\\\diverges` on function \'{func.get(\'name\', \'<anonymous>\')}\' is not justified: its body has no potentially-divergi'): '0da05801a201',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"\'\\\\result\' is not allowed in a `#@ {node.get(\'kind\')}` in {where} (it is bound only at return; use `ensures` for return'): '9cf34f251207',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Dead code in function \'{fname}\': this statement follows a call to a `NoReturn` function, which never returns normally ('): '00f0d8b19c5c',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Ghost string variable \'{target}\' does not support \'{op}\' in {where}. Use the ^ operator for string concatenation: #@ gh'): '4991961ff0d1',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Invalid use of \'\\\\result\' in {ctx}. It is only allowed in \'ensures\'.", code=\'PYCSL-SEM-RESULT\')'): 'f231be392965',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Mutable default argument in function \'{func.get(\'name\', \'<anonymous>\')}\': a list/dict/set default is a single object sh'): 'aae46c3bd27a',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"Subscript assignment to immutable \'bytes\' variable \'{arr.get(\'name\')}\' in {where} — a Python `bytes` object does not su'): '5490a176f3e0',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"\\\\length is not supported on the {typ}-typed \'{var}\' in {ctx}: dicts/sets are modelled as total maps (`map int (option '): '546b11d3b375',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' body must not `return` a value — it is a proof (returns unit). Use `pass` for an immediate arm.", c'): '327ca9d7c3e2',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' has no `#@ ensures`: a lemma must state the fact it proves (the conclusion). Add at least one `#@ e'): '9daa6cdb089f',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`#@ lemma` \'{name}\' is also `#@ \\\\diverges`: a non-terminating lemma proves nothing and would be unsound as a fact. Rem'): 'dc8a1c30dcbe',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`-> NoReturn` on function \'{name}\' is not justified: its body contains a `return` statement (a normal-exit path). A NoR'): '0e13ac56469b',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`-> NoReturn` on function \'{name}\' is not justified: its body has no `raise` and no potentially-diverging construct (no'): '6b77441c57d6',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"`happy {hname}`: method \'{m}\' contains a dynamic `exec(...)`, which may write anything (not a compile-time-constant exe'): '98d36b43a935',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"function \'{name}\' is annotated `-> str` but can `return None`. Python does not enforce the hint and the model BELIEVES '): '1b49d54c91d7',
    ("src/pycsl/core_ir_semantic.py",
     'PyCSLSemanticError(f"{where}: `#@ fresh_globals` is only allowed on a top-level driver that no other verified function calls. \'{short}\' is c'): '1924b913a4a4',
    ("src/pycsl/frontend/Module1_Ingestor.py",
     "PyCSLParseError('tabs are not allowed in `act` block indentation; use 4 spaces', stage='Module1')"): '87d9af064705',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError("a name\'s runtime binding is not the `def` the model resolves it to (" + \'; \'.join(sorted(set(_dc_bad))) + \'). A decorato'): '0d9c05bc78d3',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError("a name\'s runtime value is not the one the model reads (" + \'; \'.join(sorted(set(_nb_bad))) + \'). An imported name bound '): '9bfff38bfd6c',
    ("src/pycsl/frontend/Module3_Weaver.py",
     "PyCSLSemanticError('a function, method or class NAME is rebound after its definition (' + '; '.join(sorted(set(_rb_bad))) + '). Every call i"): '7df0d0cbe305',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Class \'{_hk_cls.name}\' (line {_hk_cls.lineno}) defines `{_hk_hit[0]}`, an attribute-access hook the model does not cons'): '6b9be60c77c2',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Class \'{node.name}\' (line {node.lineno}): `__del__` finalizer is rejected under UB-7.5. Finalizer timing is non-determi'): '917692eadfd7',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Coroutine \'{_n.name}\' (line {_n.lineno}) carries a `#@` contract, but `async def` is NOT MODELLED: the weaver attaches '): 'bc19305b45b7',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"Function \'{node.name}\' (line {node.lineno}): `#@ {_kind.lower()}` is discharged as a function-ENTRY assert over the act'): 'fd467652562a',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}({hp.param})`: \'{func_name}\' is `#@ \\\\trusted` or `#@ \\\\abstract`, is not exempt, has no `#@ footprint '): '54f350ed0da1',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}({hp.param})`: non-exempt \'{fn.name}\' performs a {kind} store to the protected path \'{path}\' (line {get'): '08c3f3300142',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: \'{func_name}\' is `#@ \\\\trusted` or `#@ \\\\abstract`, is not exempt, and its BODY writes the protected'): '392ed26344cb',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: \'{hp.target}\' is guarded by a capability precondition, but it is called here as `{_shown}.{hp.target'): '875422760137',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: aliasing the protected field \'self.{hp.field}\' into a local in non-exempt \'{fn.name}\' is forbidden —'): 'ccd00ef8e605',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: method \'{fn.name}\' contains a dynamic `exec(...)`, which may read anything — add it to `except` or r'): '102d8d091c4d',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: non-exempt \'{fn.name}\' REBINDS the whole field \'self.{hp.field}\' (line {getattr(nd, \'lineno\', 0)}), '): '19f42bdada58',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: noninterference target \'{hp.target}\' can WRITE state — `{_wfield}` in \'{_wfn}\'{_via}. The synthesize'): 'd4b62c507937',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: total target \'{hp.target}\' is marked `#@ \\\\diverges` — it opts OUT of termination, contradicting the'): 'c2d762450921',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: total target \'{hp.target}\' is marked `#@ {marker}`, so it is emitted as a bodyless `val` with no goa'): '06f5a4565f9b',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: total target \'{hp.target}\' reaches \'{_r206_hit}\', which is marked `#@ \\\\trusted`, `#@ \\\\abstract` or'): 'a525125897e3',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: trusted/abstract function \'{fn.name}\' is not exempt and has no checkable body, so it could write the'): 'e074b98b60c7',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp.name}`: trusted/abstract method \'{fn.name}\' is not exempt and its `assigns` writes a protected path ({\', \'.j'): '85917ea19250',
    ("src/pycsl/frontend/Module3_Weaver.py",
     'PyCSLSemanticError(f"`happy {hp_name}`: aliasing the protected base \'{vpath}\' into a local in non-exempt \'{cur_func or \'<module>\'}\' is forbi'): 'b9271e525001',
    ("src/pycsl/frontend/Module5_IREmitter.py",
     "PyCSLIRError('isinstance: a typing.Literal alias is not a valid second argument (LR4 / PEP 586 — use a concrete value equality test)', stage"): '0e99d9e39cac',
    ("src/pycsl/frontend/Module5_IREmitter.py",
     "PyCSLIRError(f'`\\\\forall x in {dv.coll}.items()` (two-binder) is a 07-1311 follow-on; use `.keys()`/`.values()` or the `\\\\forall k in {dv.co"): '8b610c654140',
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError("`del <obj>.<attr>` (an ATTRIBUTE delete) is not modelled: it was lowered to a bare no-op, so the model KEEPS the deleted'): '549792c165e1',
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError("`del <seq>[i:j]` (a SLICE delete) is not modelled: Python\'s slice `del` REMOVES a whole range, shifting every later elem'): '0c296648b92c',
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError("`deque(<iterable>)` with arguments is not modelled: the lowering reduces a deque to the list/array model and DISCARDS ev'): 'b50590a00fdb',
    ("src/pycsl/frontend/Module5_IREmitter.py",
     'PyCSLSemanticError(f"augmented assignment to {_aa_kind} is not modelled: this lowering handles `x op= v`, `self.f op= v`, `p.f op= v` (p a l'): 'f3f06ca2dcce',
    ("src/pycsl/frontend/desugar.py",
     'PyCSLParseError("a Python `assert` inside a `try` whose handler can catch `AssertionError` is not modelled: the `assert` is lowered to a NO-'): 'd60bfa991b0c',
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('`for ... else` / `while ... else` is not modelled: the `else` clause runs exactly when the loop finished without `break`, a"): 'dea2610de1db',
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('`try ... except*` (an exception-GROUP handler) is not modelled: `_PY_STMT_HANDLERS` has no `TryStar` entry and `_py_stmts_t"): '4e0ca212e4b8',
    ("src/pycsl/frontend/desugar.py",
     "PyCSLParseError('an EXTENDED slice `x[lo:hi:step]` is not modelled: the lowering is `Array.sub x lo (hi - lo)`, which ignores the step entir"): '07bdfae8f1a1',
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot alias module global \'{node[\'value\'][\'name\']}\' into a local (inline.md Phase 3): a global is a single named objec'): '9039261a08bf',
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\' on \'{recv}\': it has a non-tail `return` (early return / return inside a branch). Verify it by '): 'bff9068886f5',
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\' on \'{recv}\': its body refers to {\', \'.join((repr(n) for n in _cap169))}, which the calling fun'): 'f4216f102327',
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline \'{callee}\': call passes {len(args)} args, method takes {len(formals)}.")'): '74e5c1e1fab4',
    ("src/pycsl/frontend/ir_inline.py",
     'PyCSLSemanticError(f"cannot inline call to \'{recv}.{callee.split(\'__\')[-1]}\': method \'{callee}\' not found.")'): 'd13e308b1d78',
    ("src/pycsl/frontend/ir_resolve.py",
     'PyCSLSemanticError(f"Mixin \'{M}\' (composed into \'{C}\'): a method writes `self.{fld}`, a field declared neither `#@ shared_state` nor `#@ tou'): '32aade267d66',
    ("src/pycsl/frontend/ir_resolve.py",
     'PyCSLSemanticError(f"Mixin composition \'{C}\': \'{C}\' defines its own \'{pm}\', which SHADOWS the provider of \'{pm}\' (from mixin {owners}) that '): '506f3b8f1510',
    ("src/pycsl/frontend/ir_resolve.py",
     'PyCSLSemanticError(f"Mixin composition \'{C}\': dependency \'{d[\'method\']}\' (declared by mixin \'{M}\' via #@ {d[\'kind\']}_method) has NO provider'): 'ba31b3388579',
    ("src/pycsl/frontend/module5/memoization_rt.py",
     'PyCSLIRError(f"Function \'{f[\'name\']}\': a memoizing decorator (lru_cache / cache / cached_property) requires a referentially transparent func'): '0ec6687bbb52',
    ("src/pycsl/frontend/monomorphize.py",
     'PyCSLSemanticError(f"monomorphization: generic {gname!r} declares a {kind} ({tp.get(\'name\')!r}) — GT3: ParamSpec/TypeVarTuple are schema-onl'): '3d56b7df6380',
    ("src/pycsl/frontend/monomorphize.py",
     "PyCSLSemanticError(f'monomorphization: generic function {gname!r} calls itself with its own TypeVar {tvar!r} — GT4: polymorphic recursion do"): '8d67b10d57c2',
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLIRError(\'`\' + func_name + "(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstract oper'): 'c0865e444c05',
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLIRError('`' + func_name + '(...)` MUTATES an ARGUMENT in place, and no certified lowering models it: the call becomes an abstract opera"): '41fd3748d0ea',
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError('a comparison over a value that may be NaN on one path and an ordinary number on another is not modelled: NaN is the one "): 'ae832237c1f8',
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError('array/list with mixed or non-tuple elements alongside tuples is not supported: a faithful `array (tuple)` needs one unif"): 'eb0c4e9aeff6',
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"call to \'{func_name}\' passes {len(expr.get(\'args\', []))} positional argument(s) but parameter \'{nm}\' has no default (ar'): 'cb50dbe5fd40',
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"struct format \'{fmt}\': native size/alignment (\'@\' prefix) is unsupported (UB-7.4b). Native layout is platform-dependent'): 'e854f396c734',
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"the call `{func_name}(...)` resolves to a METHOD `{_sh_parts[1]}`, but instances of its class also carry an ATTRIBUTE `'): 'dd9f6f945525',
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"the call `{func_name}(...)` resolves to a METHOD `{_sh_parts[1]}`, but the program also STORES an attribute `{_sh_parts'): 'ef17bbe79799',
    ("src/pycsl/module6_whyml/expressions.py",
     'PyCSLSemanticError(f"the truthiness of `{ir_expr.get(\'name\')}` is not modelled: it is bound to {_kindname}, which this lowering emits as a v'): '1980e295d86c',
    ("src/pycsl/module6_whyml/expressions.py",
     "PyCSLSemanticError(f'heterogeneous list literal (contains a {_mix} element mixed with other element types) has no faithful WhyML `array` ele"): 'bde6249d2474',
    ("src/pycsl/module6_whyml/expressions.py",
     "_R42Err('an IDENTITY test against a `bool` literal (`X is True` / `X is False`) is refused unless the emitter can SHOW `X` is a Python `bool"): 'a722b1e33b02',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' binds %s with a `with ... as` clause, and no certified lowering models it. `_py_stmt_with` reads only the `with`'): '9768bf5fe314',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' writes %s through a `global` declaration, and no certified lowering models it: the store lands on a FRESH LOCAL '): '6b8f61032fa7',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("function \'%s\' writes %s through a `nonlocal` declaration, and no certified lowering models it. `nonlocal` has no IR statement:'): '42fa9c75fb9f',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError("nested function \'%s\' is lifted to a sibling of its enclosing function, and the lift is not faithful here: %s. A lifted body re'): 'e4a6de2819cf',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('PYCSL-SUBTYPING-PAIR: `--check-behavioral-subtyping` recorded the override pair (' + str(ov.get('sub_method')) + ' refines ' +"): 'afacce4c5ce0',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError(\'`\' + _f + \'(...)` mutates the collection PARAMETER `\' + _f.rsplit(\'.\', 1)[0] + "`, which this function\'s own contract also NAM'): '7a520ba43d1d',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` can raise `' + _r65_exc + '` in Python, and this function claims `#@ no_exception` over it. `exception_m"): '2ee0ae1ed41b',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` is not a function of the verified program and not on the list of operations known never to raise the exc"): 'b471751d0902',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` raises `ValueError` in Python on an EMPTY separator, and this function claims `#@ no_exception` over `Va"): 'd3cfbfd0ea38',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(...)` resolves to a `#@ \\\\trusted` or `#@ \\\\abstract` method of this program, and this function claims `#@ no_"): 'a9696cdf90f1',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r65_f + '(<str>)` raises `ValueError` in Python on a non-numeric string, and this function claims `#@ no_exception` over"): 'f6a9dba445a9',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _r71_f + '(...)` can raise `KeyError` in Python, and this function claims `#@ no_exception` over it — but the mutation of"): '5d6e875abc70',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`' + _x178['func'] + '(...)` calls code that can raise `' + '`/`'.join(_hit178) + '` implicitly (a dict or list subscript, an "): '8d58ae379a39',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError(\'`\' + str(_r63_n.get(\'func\')) + \'(...)` is passed the SAME dict/set `\' + _r63_nm + "` in more than one argument position. In Py'): '883441549356',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError('`ord(...)` over a NON-ASCII string is out of scope: PyCSL emits a string literal as its UTF-8 BYTES and models characters with"): 'ece5445ae54a',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLIRError(\'the collection PARAMETER `\' + _r62_p + "`, which this function\'s contract NAMES, is passed to `" + str(_r62_n.get(\'func\')) + "'): '68f46b4c7d3f',
    ("src/pycsl/module6_whyml/functions.py",
     "PyCSLIRError(_r160_msg + ', and this function claims `#@ no_exception` over it. There is no trigger row for this builtin and no faithful obl"): '5a8a04f805d4',
    ("src/pycsl/module6_whyml/functions.py",
     'PyCSLSemanticError(f"storing a mutated dict into a field is out of scope: `{_s.get(\'object\')}.{_s.get(\'field\')} = {_pname}` binds the field '): '0dbf57de0b3e',
    ("src/pycsl/module6_whyml/preamble.py",
     "PyCSLIRError(f'#@ proof {qn}: not in Module6 axiom registry. Either add the axiom body to _AXIOM_REGISTRY or run `proof2why3 emit` (when ava"): '8505e4a9a547',
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLIRError('PYCSL-UNFRAMED-REGION-ASSIGNS: this function is emitted as a bodyless `val` (a `\\\\trusted` / `\\\\abstract` / imported stub) and"): '940cd78f51a2',
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLIRError('`' + func + '(...)` appends to the collection in the field `' + func.split('.')[1] + '`, and no certified lowering models it: "): '782d26097a22',
    ("src/pycsl/module6_whyml/statements.py",
     'PyCSLIRError(\'`del \' + (arr.get(\'name\') or \'<expr>\') + "[...]` on a non-dict/set receiver is not modelled: Python\'s list `del` SHIFTS every '): '9a6f83140d1f',
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError('an `assert` whose TEST may have a SIDE EFFECT is not modelled: the test is lowered to `()`, i.e. DISCARDED, so any mutat"): '055333eadf1e',
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError(f'aliasing a mutated dict is out of scope: `{target} = {_alias_of}` binds a SECOND NAME TO THE SAME dict in Python, and a"): 'd2e76aef956c',
    ("src/pycsl/module6_whyml/statements.py",
     "PyCSLSemanticError(f'in-place field mutation `{obj}.{field} = ...` of a record whose class `{_obj_cls}` is used as a `List[<record>]` elemen"): 'abcdf79520c2',
    ("src/pycsl/module6_whyml/statements.py",
     '_R49("in-place `append` to list parameter \'%s\' is out of scope: Python passes a list argument BY REFERENCE, so the append must be VISIBLE to'): 'eb1056d01f66',
    ("src/pycsl/module6_whyml/statements.py",
     '_R49B("in-place `%s=` on list parameter \'%s\' is out of scope: Python `a += b` on lists is an IN-PLACE extend, so the caller\'s list grows, an'): 'a673392745af',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr179(f"{_d179.name!r} constructs an object whose `__init__` / `__post_init__` can raise `{_e179}` (ROUTE #179), directly or throu'): '9f8110fb27ba',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr187(f"this module declares `#@ fresh_globals`, which ASSUMES each module-global singleton\'s constructor post-state at the driver'): 'fba5cac5b014',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr189(f"{_fd189.name!r} binds {_nm189!r} to more than one class ({\', \'.join(sorted(_bd189[_nm189]))}) and then calls `{_nm189}.{_c'): '57dcba462a27',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr200(f"in \'{_r200_caller}\': the call to \'{_r200_fn}\' passes a string literal to parameter \'{_r200_pname}\', which \'{_r200_fn}\' dec'): '52ea50981615',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr204(f"{args.file} (function \'{_f204.get(\'name\')}\'): the `#@ interface assigns` frame is NARROWER than the definition\'s `#@ assig'): '38b31375f86c',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr212(f"{args.file}: `--verify-imports` was given and the imported module \'{_mod212}\' ({_path212}) does NOT verify, so none of its'): '7f2282764908',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr215(f"{args.file} (line {getattr(_n215, \'lineno\', 0)}): `{_n215.func.value.id}[...](...)` SUBSCRIPTS A GENERIC FUNCTION at a cal'): 'ce1ac8c11fc8',
    ("src/pycsl/pycsl.py",
     "_PyCSLSemErr29(f'the array spec atom `{_r29_names[_r29_hit]}` is not interpreted under the {memory_model!r} memory model (ROUTE #29): its Mo"): '8da2d97e88eb',
    ("src/pycsl/pycsl.py",
     "_PyCSLSemErr38('a `with` statement in a file that defines a context-manager class (%s) uses a context expression this build cannot positivel"): 'bcf10a03319b',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemErr43("a COMPLEX literal (%r) has no model (ROUTE #43): `_py_expr_constant` lowers it to `int(value.real)`, so the imaginary part i'): '2b425e50069d',
    ("src/pycsl/pycsl.py",
     '_PyCSLSemanticError(f"{args.file} (function \'{_func.get(\'name\')}\', for-loop near line {v.get(\'loop_line\', \'?\')}): UB-7.1 — the loop body mut'): '14c833a221e3',
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
            # (#49) RESOLVE IMPORT ALIASES — the same artifact found in
            # `check-refusal-witness-coverage` the same evening. Twenty-one raises in
            # this compiler import the exception class under a local alias
            # (`from errors import PyCSLSemanticError as _PyCSLSemErr204`), and a filter
            # keyed on the raised NAME excludes every one of them. They are
            # disproportionately the CURRENT campaign's own work, because new code is
            # written in whatever local style it needed. Fixed here too rather than left
            # inconsistent between two planes that census the same population.
            _alias = {}
            for _n in ast.walk(tree):
                if isinstance(_n, (ast.Import, ast.ImportFrom)):
                    for _a in _n.names:
                        if _a.asname and str(_a.name).startswith("PyCSL"):
                            _alias[_a.asname] = _a.name
            for n in ast.walk(tree):
                if not isinstance(n, ast.Raise) or not isinstance(n.exc, ast.Call):
                    continue
                nm = getattr(n.exc.func, "id", None) or getattr(n.exc.func, "attr", None)
                if not nm:
                    continue
                if not str(nm).startswith("PyCSL") and nm not in _alias:
                    continue
                raises += 1
                msg = " ".join(literal_parts(n.exc))
                if ADVICE.search(msg):
                    _src = " ".join(ast.unparse(n.exc).split())
                    advice.append((os.path.relpath(f, ROOT), n.lineno, msg[:90],
                                   sig(n.exc),
                                   hashlib.sha256(_src.encode()).hexdigest()[:12]))
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

    keys = {(f, sg) for f, _ln, _m, sg, _h in advice}
    hash_of = {(f, sg): h for f, _ln, _m, sg, h in advice}
    line_of = {(f, sg): ln for f, ln, _m, sg, _h in advice}
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
        for f, ln, m, sg, _h in sorted(advice):
            if (f, sg) in AUDITED:
                if args.verbose:
                    print("    %-12s %s:%d" % (AUDITED[(f, sg)][0], f, ln))
            else:
                print("    unaudited    %s:%d  %s" % (f, ln, m[:60]))

    rc = 0
    edited = [k for k in done
              if k in AUDITED_HASH and hash_of.get(k) != AUDITED_HASH[k]]
    for f, sg in sorted(edited):
        print("[!]   MESSAGE EDITED SINCE ITS AUDIT: %s / %r. The key still matches (the "
              "first 140 characters are unchanged) but the MESSAGE HASH does not, and a "
              "refusal's advice lives at the END. Re-run the audit — write the program "
              "the NEW message describes — and update the entry and its hash."
              % (f, sg[:60]), file=sys.stderr)
        rc = 1
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
              "had their advice FOLLOWED and run (floor %d)%s"
              % (len(done), len(advice), MIN_AUDITED,
                 "." if not todo else
                 ". The remaining %d are unaudited, which is a debt this plane exists to "
                 "make visible rather than a failure." % len(todo)))
    return rc


MIN_AUDITED = 113

if __name__ == "__main__":
    sys.exit(main())
