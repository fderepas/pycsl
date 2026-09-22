#!/usr/bin/env python3
r"""L-PLANE ORACLE: a `pycsl_lib` function whose body is `return <a parameter>` and whose
contract PINS that identity.

WHY THIS EXISTS (gen #30, the THIRD stdlib plane). The first two cover the two shapes I
had found: `check-stdlib-contract-fidelity.py` CALLS the real function (so it carries a
safety deny-list and can only reach pure modules), and `check-stdlib-pinned-facades.py`
covers, statically, the bodies that are a single CONSTANT pinned by their own contract.
Widening the fidelity map in gen #30 turned up SIX diverging functions that are neither:
`ctxlib.closing/contextmanager/nullcontext`, `ftools.lru_cache/wraps`, `pp.saferepr`. Their
shape is

    #@ ensures \result == func
    def wraps(func):
        return func

— the body is the IDENTITY on a parameter and the contract pins it. The contract is true
of the body and FALSE of the function the module's own header cites: real
`functools.wraps` returns a `functools.partial` of `update_wrapper`, real
`contextlib.closing` returns a context-manager OBJECT, real `pprint.saferepr` returns a
STRING. A user who proves `ftools.wraps(g) == g` has proven something CPython contradicts.

WHY A PLANE AND NOT SIX BASELINE ENTRIES. Because the shape is POPULOUS and most of it is
OUT OF THE CALLING GATE'S REACH. The census finds 82 of them across 30 packages, and they
sit in `os`, `shutl`, `pkl`, `rng`, `hmacmod` — modules the fidelity gate must never call.
So the six that were caught were caught by ACCIDENT OF PURITY, not by coverage: the same
defect in `shutl.move` (real `shutil.move` returns the DESTINATION path, not `src`) can
never be found by calling. This gate is the static complement, exactly as the facade gate
is for constants.

NOT EVERY MEMBER IS A DEFECT, and the gate does not pretend otherwise. `mth.fabs` under
`requires x >= 0` IS the identity; `typ.cast` really does return its value; `astmod`'s
in-place transformers really do return the node they were handed. The population splits
three ways and each entry says which it is:

  FAITHFUL   — the real function really is the identity here (or is under the stated
               precondition). Sound, and it stays sound.
  DIVERGES   — the real function returns something else. Already PROVEN so by the calling
               gate, and cross-checked here: every DIVERGES entry in a module the fidelity
               map covers must also appear in THAT gate's baseline, or this gate fails.
  DIVERGES-BY-HAND — the real function returns something else, proven by ONE specific,
               safe, RECORDED call (`shutil.copy(a, b)` returns `b`; `struct.pack('i', 0)`
               returns bytes; `os.fsencode('a')` returns `b'a'`). This is how a stub gets
               adjudicated when the pool-driven gate cannot evaluate its contract or must
               never call its module. Kept distinct from DIVERGES so the cross-check below
               stays meaningful.
  DECLARED-DOMAIN — the stub models a DIFFERENT, DECLARED quantity (a size, a count, a
               length), not the cited function's return value; the declaration is in the
               signature AND the docstring, and the claim about that quantity is MEASURED
               true of CPython. The block comment above the class constants says why this
               is kept distinct from DIVERGES-BY-HAND rather than folded into it.
  MODEL-INTERNAL — no cited CPython function exists (a leading-underscore helper of the
               model itself), so the obligation is the stub's own guard, which the entry
               must name.
  UNADJUDICATED — the module is outside the calling gate's reach and no one has ruled on
               it yet. This was the honest state for most of the population, and it was
               WRITTEN DOWN rather than left as an unmentioned gap — the gen #30 lesson
               from the fidelity plane's own scope claim ("an unmentioned exclusion is not
               an exclusion, it is an oversight wearing one"). **The class is now EMPTY**:
               the second pass adjudicated all 24 and MAX_UNADJUDICATED is 0.

THE STANDING COUNT after the second pass: 81 stubs — 33 FAITHFUL, 6 DIVERGES, 25
DIVERGES-BY-HAND, 15 DECLARED-DOMAIN, 2 MODEL-INTERNAL, 0 UNADJUDICATED. So **31 of the 81
carry a contract that is FALSE of the function the stub's own header cites**, and only six
of those were reachable by calling. That ratio is the argument for this gate.

WHAT THE SECOND PASS ACTUALLY FOUND, since clearing a debt counter is not by itself a
result. Seven of the 24 turned out to be genuinely false, and were MEASURED so rather than
reasoned so: `csvmod.write_row` (writerow returns a CHARACTER count, 7, not the 3 fields —
and the stub's own docstring says ">= field count" while its contract pins "=="),
`cvar.context_var_get` (`cv.get(0)` is 5 after `cv.set(5)`), `cvar.context_var_set`
(returns a `Token`), `dec.getcontext_prec` (unbounded above, and `prec = 10**30` RAISES
`OverflowError` past `decimal.MAX_PREC`), `nums.rational_num` / `rational_den`
(`Fraction(2, 4).numerator` is 1, not 2 — the guards `num >= 0` / `den > 0` do not imply
the coprimality the claim needs), and `os.getenv` (`os.getenv('PATH', 0)` is not 0; the
empty-env justification lives in a COMMENT, which is not a contract). Fifteen are a
declared size/count/length law and were measured TRUE — with one residual written into the
entries: the three `hq.*_max` stubs take a `heap: list` and an `n: int` and never tie them,
so their size law is true but VACUOUS.

AND ONE OF THEM MOVED THE SAME DAY IT WAS WRITTEN. `strmod.capwords` was classified
FAITHFUL on the strength of its guards; mining the axiom registry then showed the OTHER
clause on the same function — the length bound — is false of CPython for `'ß'`. A
classification is a claim too, and "the clause I looked at is guarded" is not "the function
is faithful".

THE RATCHET is the set, keyed by (package, function). A NEW identity-stub fails: it must
be argued into one of the three classes. One that DISAPPEARS is reported so its entry goes
with it. UNADJUDICATED is a debt counter, printed every run, and MAX_UNADJUDICATED holds
it from growing.

THE POPULATION GUARD (the #44 rule): rc=2 if the walk sees fewer than MIN_FUNCTIONS
functions at all, so "no identity stubs" can never mean "I parsed nothing".

Usage:  bin/check-stdlib-identity-stubs.py [--verbose] [--selftest-empty-baseline]
"""
import argparse
import ast
import glob
import os
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
MIN_FUNCTIONS = 700      # 870 at the first measurement
MIN_STUBS = 70           # 82 at the first measurement; the stub set only grows

FAITHFUL, DIVERGES, UNADJ = "FAITHFUL", "DIVERGES", "UNADJUDICATED"
# A FOURTH class, added in the same generation as the plane. HAND is a divergence proven
# by ONE specific, safe, recorded call rather than by the pool-driven calling gate — the
# route for a stub whose contract the pool cannot evaluate (`struct.pack` needs a real
# format string) or whose module that gate must never call (`shutil`, `os`). Its entries
# carry the measured answer verbatim, so the claim is checkable by rerunning one line.
# It is kept DISTINCT from DIVERGES on purpose: DIVERGES means "the calling gate agrees
# and has it baselined", and the cross-check below enforces exactly that, so folding
# hand-measured results into it would make the two planes look like they disagree when
# they simply never evaluated the same thing.
HAND = "DIVERGES-BY-HAND"

# Gen #30, second adjudication pass. Two classes the first pass did not have, and whose
# absence is why 24 entries sat in UNADJUDICATED behind a one-line "no citation run".
#
# DECLARED-DOMAIN - the stub does not model the cited function's RETURN VALUE AT ALL. It
#   models a DIFFERENT, DECLARED quantity (a size, a count, a length); the declaration is
#   visible in the SIGNATURE (an `int` parameter named `n`/`size`/`digest_size` where the
#   real function takes a container) AND in the module or function docstring; and the
#   claim about that quantity is TRUE OF CPYTHON AND MEASURED. This is exactly the reading
#   `pkl.dump`'s entry reasons about and REJECTS - "the honest reading is a declared
#   domain change, but it is UNDECLARED, which is the defect". Keeping the two classes
#   apart makes that discriminator executable instead of rhetorical: declared AND measured
#   lands here; undeclared stays DIVERGES-BY-HAND.
# MODEL-INTERNAL - there is NO cited CPython function (a leading-underscore helper of the
#   model itself), so there is nothing to be faithful to and nothing to diverge from. The
#   obligation is instead that the stub's OWN guard makes the identity true of the model it
#   defines, and the entry must NAME that guard.
DECLARED = "DECLARED-DOMAIN"
INTERNAL = "MODEL-INTERNAL"

# (package, function) -> (class, why)
BASELINE = {
    # ---- DIVERGES: proven false against the real function by the calling gate.
    ("ctxlib", "closing"): (DIVERGES,
        "real `contextlib.closing` returns a closing CONTEXT MANAGER wrapping obj."),
    ("ctxlib", "contextmanager"): (DIVERGES,
        "real `contextlib.contextmanager` returns a generator-driven HELPER function."),
    ("ctxlib", "nullcontext"): (DIVERGES,
        "real `contextlib.nullcontext` returns a nullcontext OBJECT, not the value."),
    ("ftools", "lru_cache"): (DIVERGES,
        "real `functools.lru_cache` returns a DECORATING FUNCTION."),
    ("ftools", "wraps"): (DIVERGES,
        "real `functools.wraps` returns a `functools.partial` of `update_wrapper`."),
    ("pp", "saferepr"): (DIVERGES,
        "real `pprint.saferepr` returns the STRING repr — `saferepr(0)` is `'0'`."),

    # ---- FAITHFUL: the real function is the identity, here or under the precondition.
    ("mth", "fabs"): (FAITHFUL, "`requires x >= 0`, so `abs(x) == x`."),
    ("mth", "floor"): (FAITHFUL, "integer model: `floor` of an int is the int."),
    ("mth", "ceil"): (FAITHFUL, "integer model: `ceil` of an int is the int."),
    ("mth", "trunc"): (FAITHFUL, "integer model: `trunc` of an int is the int."),
    ("oper", "pos"): (FAITHFUL, "`operator.pos(x)` is `+x`, the identity on ints."),
    ("oper", "abs_val"): (FAITHFUL, "guarded by `requires x >= 0` in the stub."),
    ("oper", "index"): (FAITHFUL, "`operator.index` of an int is that int."),
    ("nums", "to_int"): (FAITHFUL, "int of an int."),
    ("typ", "cast"): (FAITHFUL, "`typing.cast(t, v)` really does return `v` unchanged."),
    ("typ", "Union"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "Literal"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "Final"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "TypedDict"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "NamedTuple"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "overload"): (FAITHFUL, "`typing.overload` returns the function it decorates."),
    ("typ", "runtime_checkable"): (FAITHFUL,
        "`typing.runtime_checkable` returns the class it decorates."),
    ("astmod", "copy_location"): (FAITHFUL, "`ast.copy_location` returns `new_node`."),
    ("astmod", "fix_missing_locations"): (FAITHFUL,
        "`ast.fix_missing_locations` returns the node it was handed."),
    ("astmod", "increment_lineno"): (FAITHFUL, "`ast.increment_lineno` returns the node."),
    ("abcmod", "abstractmethod"): (FAITHFUL,
        "`abc.abstractmethod` returns the function, with `__isabstractmethod__` set."),
    ("cpmod", "copy"): (FAITHFUL,
        "in the INTEGER model a copy is `==` to its original, which is all the contract "
        "claims; the calling gate agrees on the pool."),
    ("cpmod", "deepcopy"): (FAITHFUL, "same as `copy` in the integer model."),
    ("gettext_stub", "gettext"): (FAITHFUL,
        "with no catalogue installed, `gettext.gettext(s)` returns `s`."),
    ("htmlm", "escape"): (FAITHFUL, "the contract is GUARDED (`s == 0 ==> ...`), not a "
        "bare identity; the empty/0 case is the one it pins."),
    ("htmlm", "unescape"): (FAITHFUL, "guarded the same way."),
    ("htmlm", "escape_quote"): (FAITHFUL, "guarded the same way."),
    ("txtwrp", "fill"): (FAITHFUL, "guarded (`text == 0 ==> \\result == 0`)."),
    ("strmod", "capwords"): (HAND,
        "WAS classified FAITHFUL here on the strength of its guards; gen #30 MEASURED the "
        "OTHER clause on the same function and it is FALSE of CPython. The model carries "
        "`#@ ensures sep == \"\" ==> \\str_length(\\result) <= \\str_length(s)` and the "
        "imported axiom `Pycsl.Strmod.Capwords.capwords_length_nongrowing` says the same "
        "thing, with the preamble comment justifying it as \"capitalize (first upper, "
        "rest lower; LENGTH-PRESERVING)\". MEASURED: `string.capwords(\'\\u00df\')` is "
        "`\'Ss\'` (1 -> 2) and `string.capwords(\'\\ufb01\')` is `\'Fi\'` — "
        "`str.capitalize()` is not length-preserving for characters with multi-character "
        "uppercase forms. The calling gate cannot catch it because the model encodes the "
        "DEFAULT separator as `sep == \"\"` while CPython\'s default is `None` and "
        "`capwords(s, \"\")` raises ValueError, so the guarded clause is unfalsifiable "
        "against the real function. NOT a route: the model\'s own body returns the string "
        "unchanged, so a program proved against it agrees with CPython when CPython runs "
        "THE MODEL. It is a fidelity defect of the model and a false axiom about the "
        "real function."),
    ("wref", "ref"): (FAITHFUL,
        "MODEL-DOMAIN identity: the stub's `ref` carries the referent through because the "
        "integer model has no weak references; the calling gate evaluates it and the "
        "contract holds on the pool. Re-open if the model ever grows real references."),
    ("wref", "proxy"): (FAITHFUL, "same model-domain argument as `ref`."),

    # ---- UNADJUDICATED: outside the calling gate's reach, not yet ruled on.
    ("abcmod", "abstractclassmethod"): (HAND,
        "MEASURED: `type(abc.abstractclassmethod(g)).__name__` is `abstractclassmethod` "
        "and `abc.abstractclassmethod(g) is g` is False — it returns a DESCRIPTOR."),
    ("abcmod", "abstractstaticmethod"): (HAND,
        "MEASURED: returns an `abstractstaticmethod` descriptor, not the function."),
    ("abcmod", "update_abstractmethods"): (FAITHFUL,
        "MEASURED: `abc.update_abstractmethods(int) is int` is True."),
    ("copyreg", "constructor"): (HAND,
        "MEASURED: `copyreg.constructor(len)` returns None, not the callable."),
    ("csvmod", "write_row"): (HAND,
        "MEASURED on an `io.StringIO` (no filesystem, so the deny-list was never in the "
        "way): `csv.writer(sio).writerow(['a','b','c'])` returns 7 - the CHARACTER count "
        "of `'a,b,c\\r\\n'` - not the 3 fields the contract pins. The stub's OWN "
        "docstring says 'Written bytes >= field count' while its `#@ ensures` pins "
        "`== num_fields`: docstring and contract contradict each other, and the docstring "
        "is the one that is right."),
    ("cvar", "context_var_get"): (HAND,
        "MEASURED: after `cv.set(5)`, `cv.get(0)` is 5, not 0. The docstring says "
        "'returns default if not set' but the `#@ ensures \\result == default` is "
        "UNCONDITIONAL, so it is false of exactly the case the variable exists for. Same "
        "shape as `os.getenv`."),
    ("cvar", "context_var_set"): (HAND,
        "MEASURED: `ContextVar.set(5)` returns a `Token` (what `reset` consumes), not "
        "the value 5."),
    ("dec", "getcontext_prec"): (HAND,
        "MEASURED: the set-then-get round trip holds for small values (`prec = 5` reads "
        "back 5), but the stub guards only `requires prec > 0`, and "
        "`getcontext().prec = 10**30` RAISES `OverflowError` (`decimal.MAX_PREC` is "
        "999999999999999999). So the unconditional `ensures \\result == prec` is false "
        "above MAX_PREC - a RAISE divergence rather than a different value, still a fact "
        "CPython contradicts. CLOSING IT = `requires prec <= 999999999999999999`."),
    ("ftools", "partial"): (HAND,
        "MEASURED: `type(functools.partial(len)).__name__` is `partial` — an object that "
        "is not the function and does not compare equal to it."),
    ("ftools", "cache"): (HAND,
        "MEASURED: `type(functools.cache(len)).__name__` is `_lru_cache_wrapper`. Same "
        "family as `lru_cache`; the pool gate never evaluated this one."),
    ("hmacmod", "new_hmac"): (DECLARED,
        "DECLARED: module header 'Models HMAC as digest-size tracker'; parameters "
        "`key_len`/`digest_size`; docstring 'Create HMAC object, return digest size'. "
        "MEASURED: `len(hmac.digest(b'k', b'm', 'sha256'))` is 32, the sha256 digest "
        "size - the modelled quantity is real and the claim about it is true."),
    ("hmacmod", "digest"): (DECLARED,
        "Same declaration and the same measurement as `new_hmac`."),
    # The heapq family: a SIZE LAW, declared in every signature (`n: int` / `size: int`
    # where real heapq takes a list) and in every docstring ("Size unchanged", "The heap
    # size doesn't change", "(count model)"). MEASURED against this CPython: heapify,
    # heappushpop and heapreplace all leave `len(heap)` unchanged; `len(nsmallest(2, xs))`
    # and `len(nlargest(2, xs))` are 2 under the stubs' own `requires n <= size`; and the
    # three private max-heap entry points `_heapify_max`, `_heappushpop_max` and
    # `_heapreplace_max` all EXIST (checked by `hasattr`, so the `_max` stubs are not
    # modelling functions that are not there) and preserve size too.
    ("hpq", "heappushpop"): (DECLARED, "size law; measured, size preserved."),
    ("hpq", "heapreplace"): (DECLARED, "size law; measured, size preserved."),
    ("hpq", "heapify"): (DECLARED, "size law; measured, size preserved."),
    ("hpq", "nsmallest"): (DECLARED,
        "count law under the stub's own `requires n <= size`; measured `len(...) == n`."),
    ("hpq", "nlargest"): (DECLARED, "count law; measured the same way as `nsmallest`."),
    ("hq", "heapreplace"): (DECLARED,
        "size law; and `requires n >= 1` matches the IndexError real `heapreplace` "
        "raises on an empty heap."),
    ("hq", "heapify"): (DECLARED, "size law; measured, size preserved."),
    ("hq", "heappushpop"): (DECLARED, "size law; measured, size preserved."),
    # RESIDUAL, and it is the thing this class must not be allowed to hide: the three
    # `_max` stubs take BOTH `heap: list` AND `n: int` and never tie them - no clause says
    # `\\length(heap) == n`. So `\\result == n` is TRUE but VACUOUS as a size law: a caller
    # may hand a 3-element heap and `n = 99` and prove 99. Under-specified, not false; the
    # repair is a `requires`, not a reclassification.
    ("hq", "heapify_max"): (DECLARED, "size law; `heap` and `n` are not tied (see above)."),
    ("hq", "heappushpop_max"): (DECLARED, "size law; `heap` and `n` are not tied."),
    ("hq", "heapreplace_max"): (DECLARED, "size law; `heap` and `n` are not tied."),
    ("itools", "count_n"): (DECLARED,
        "LENGTH law, declared by the module header ('we model them by their output "
        "LENGTH') and by the `_n` suffix on a name real itertools does not have. "
        "MEASURED: `len(list(islice(count(3), 4)))` is 4."),
    ("itools", "repeat_n"): (DECLARED,
        "LENGTH law; MEASURED: `len(list(repeat(7, 4)))` is 4."),
    ("nums", "rational_num"): (HAND,
        "MEASURED: `Fraction(2, 4).numerator` is 1, NOT 2. The stub returns the `num` it "
        "was handed under `requires num >= 0` / `requires den > 0` - guards that do NOT "
        "imply coprimality, which is what the claim actually needs; its docstring cites "
        "'Rational has .numerator property', so the cited function is the NORMALISING "
        "one. CLOSING IT = a coprimality `requires`, or a contract about the reduced "
        "pair."),
    ("nums", "rational_den"): (HAND,
        "MEASURED: `Fraction(2, 4).denominator` is 2, NOT 4. The same missing "
        "coprimality guard as `rational_num`; the `ensures \\result > 0` half is fine."),
    ("os", "_encode_name"): (INTERNAL,
        "LEADING UNDERSCORE: there is no `os._encode_name` in CPython, so there is no "
        "cited function to diverge from - this is the model's own directory-entry name "
        "field codec. The identity is made true of the model by the stub's OWN guard "
        "`requires \\str_length(name) <= 30`, which is what keeps the 30-byte field "
        "TRUNCATION out of the domain; without it the pinned identity would hide exactly "
        "that truncation. Guard named, so the entry is honest."),
    ("os", "_decode_name"): (INTERNAL,
        "The other half of the same model-internal codec; `_encode_name`'s guard is what "
        "makes the pair's round-trip compose. NOTE THE ASYMMETRY: `_decode_name` carries "
        "NO length guard of its own, so it is the identity on a stored field of ANY "
        "length - sound only because nothing in the model can store one longer than 30."),
    ("os", "fsdecode"): (FAITHFUL,
        "MEASURED: `os.fsdecode(\'a\')` is `\'a\'`. Identity on `str`, which is this "
        "model\'s whole domain; on `bytes` it decodes, and the model has no bytes."),
    ("os", "fsencode"): (HAND,
        "MEASURED: `os.fsencode(\'a\')` is `b\'a\'` — BYTES, which does not equal the "
        "`str` it was given."),
    ("os", "fspath"): (FAITHFUL,
        "MEASURED: `os.fspath(\'a\')` is `\'a\'`; identity on `str`."),
    ("os", "getenv"): (HAND,
        "MEASURED: `os.getenv('PATH', 0)` is not 0 - it is the PATH string. The "
        "`ensures \\result == default` is UNCONDITIONAL and its justification lives in a "
        "COMMENT ('this model has an empty env'), which is not a contract. Sound only "
        "for a caller who also believes the env is empty, and nothing makes them."),
    ("os", "expanduser"): (HAND,
        "MEASURED: `os.path.expanduser(\'~/x\')` is `\'/home/<user>/x\'`, not `\'~/x\'`. "
        "The stub\'s `#@ interface ensures \\result == path` is unqualified and so is "
        "false of exactly the inputs the function exists for."),
    ("pkl", "dump"): (HAND,
        "MEASURED: `pickle.dump(0, f)` returns None. The stub models the SIZE, so the "
        "honest reading is a declared domain change — but it is undeclared, which is the "
        "defect: nothing in the stub says `\\result` is a size rather than the object."),
    ("pp", "pformat"): (HAND,
        "MEASURED: `pprint.pformat(0)` is the STRING `\'0\'`, like `saferepr`. Two stubs "
        "share this name in the package (one on `obj`, one on `obj_size`); the pool gate "
        "evaluated neither."),
    ("rng", "sample_len"): (FAITHFUL,
        "`random.sample(pop, k)` is non-deterministic in its CONTENT but its LENGTH is "
        "exactly `k`, and `k` is all this stub returns. The deny-list keeps the calling "
        "gate out; the length claim needs no call."),
    ("shutl", "copy"): (HAND,
        "MEASURED in a scratch directory: `shutil.copy(a, b)` returns `b`, the "
        "DESTINATION. The contract pins `src`."),
    ("shutl", "copy2"): (HAND, "MEASURED: `shutil.copy2(a, c)` returns `c`."),
    ("shutl", "move"): (HAND, "MEASURED: `shutil.move(c, d)` returns `d`."),
    ("strct", "calcsize"): (HAND,
        "MEASURED: `struct.calcsize(\'i\')` is 4 — a SIZE, not the format it was given."),
    ("strct", "pack"): (HAND,
        "MEASURED: `struct.pack(\'i\', 0)` is `b\'\\x00\\x00\\x00\\x00\'` — BYTES."),
    ("strct", "unpack"): (HAND,
        "MEASURED: `struct.unpack(\'i\', b\'\\0\'*4)` is `(0,)` — a TUPLE."),
    ("strct", "unpack_from"): (HAND, "same TUPLE answer as `unpack`."),
    ("strct", "pack_into"): (HAND, "`struct.pack_into` writes into a buffer and returns None."),
}
MAX_UNADJUDICATED = 0    # 45 at the first measurement, 24 after the same-day hand
                         # adjudication, 0 after the second pass added the two classes
                         # above. A debt that may only shrink - and at zero it is also a
                         # RATCHET: a new stub can no longer be parked here.


def census():
    """Every (package, function, param) whose body is `return <param>` under a pinning
    `#@ ensures` that mentions that parameter. Pure AST; nothing is imported or called."""
    stubs, functions = [], 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for path in sorted(glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True)):
            src = open(path, encoding="utf-8").read()
            lines = src.splitlines()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            pkg = os.path.basename(os.path.dirname(path))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                functions += 1
                body = [n for n in node.body
                        if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                                and isinstance(n.value.value, str))]
                if len(body) != 1 or not isinstance(body[0], ast.Return):
                    continue
                ret = body[0].value
                if not isinstance(ret, ast.Name):
                    continue
                params = [a.arg for a in node.args.args if a.arg != "self"]
                if ret.id not in params:
                    continue
                ann = []
                i = node.lineno - 2
                while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith("#")):
                    if lines[i].strip().startswith("#@"):
                        ann.append(lines[i].strip())
                    i -= 1
                if any("ensures" in a and "\\result ==" in a for a in ann):
                    stubs.append((pkg, node.name, ret.id))
    return stubs, functions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-empty-baseline", action="store_true",
                    help="run with an EMPTY baseline; must exit 1 (proves the gate bites)")
    args = ap.parse_args()

    baseline = {} if args.selftest_empty_baseline else BASELINE
    stubs, functions = census()

    if functions < MIN_FUNCTIONS:
        print("[!] stdlib-identity-stubs: REFUSING — the walk saw only %d function(s), "
              "expected at least %d. The glob is broken; this is not a pass."
              % (functions, MIN_FUNCTIONS), file=sys.stderr)
        return 2
    if len(stubs) < MIN_STUBS and not args.selftest_empty_baseline:
        print("[!] stdlib-identity-stubs: REFUSING — %d identity stub(s) found, expected "
              "at least %d. The matcher is broken; this is not a pass."
              % (len(stubs), MIN_STUBS), file=sys.stderr)
        return 2

    keys = {(p, f) for p, f, _ in stubs}
    new = sorted(k for k in keys if k not in baseline)
    gone = sorted(k for k in baseline if k not in keys)
    unadj = sorted(k for k in keys if baseline.get(k, (None,))[0] == UNADJ)
    diverges = sorted(k for k in keys if baseline.get(k, (None,))[0] == DIVERGES)
    hand = sorted(k for k in keys if baseline.get(k, (None,))[0] == HAND)
    decl = sorted(k for k in keys if baseline.get(k, (None,))[0] == DECLARED)
    intl = sorted(k for k in keys if baseline.get(k, (None,))[0] == INTERNAL)

    if args.verbose:
        for p, f, a in sorted(stubs):
            cls = baseline.get((p, f), ("NEW", ""))[0]
            print("    %-13s %-9s %-22s <- %s" % (cls, p, f, a))

    print("[*] stdlib-identity-stubs: %d function(s) scanned; %d identity stub(s) with a "
          "pinning contract; %d DIVERGES, %d DIVERGES-BY-HAND, %d DECLARED-DOMAIN, "
          "%d MODEL-INTERNAL, %d UNADJUDICATED."
          % (functions, len(keys), len(diverges), len(hand), len(decl), len(intl),
             len(unadj)))

    rc = 0
    # Cross-check: a DIVERGES in a module the CALLING gate covers must also be in ITS
    # baseline, or the two planes disagree about the same function.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_fid", os.path.join(ROOT, "bin", "check-stdlib-contract-fidelity.py"))
        fid = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fid)
        for k in diverges:
            if k[0] in fid.MAP and k not in fid.BASELINE:
                print("[!]   %s.%s is DIVERGES here but is NOT in the calling gate's "
                      "baseline, and its module IS in that gate's map. The two planes "
                      "disagree." % k, file=sys.stderr)
                rc = 1
    except Exception as exc:                                  # pragma: no cover
        print("[!]   cross-check against the calling gate failed: %r" % (exc,),
              file=sys.stderr)
        rc = 1

    for k in gone:
        print("[+]   baselined identity stub %s.%s IS GONE — remove its entry." % k)
    for k in new:
        print("[!]   NEW IDENTITY STUB %s.%s — a body `return <param>` pinned by its own "
              "`ensures`. Argue it into FAITHFUL (the real function IS the identity), "
              "DIVERGES (it is not, and the calling gate agrees), DIVERGES-BY-HAND (it is "
              "not, proven by one recorded call), DECLARED-DOMAIN (it models a DIFFERENT "
              "quantity, the signature AND the docstring say so, and the claim about that "
              "quantity is measured true) or MODEL-INTERNAL (no cited CPython function "
              "exists; name the guard that makes the identity true of the model), and add "
              "it to the baseline. UNADJUDICATED is CLOSED: its ceiling is 0."
              % k, file=sys.stderr)
        rc = 1
    if len(unadj) > MAX_UNADJUDICATED:
        print("[!]   UNADJUDICATED count %d exceeds the ceiling %d — this debt may only "
              "shrink." % (len(unadj), MAX_UNADJUDICATED), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] stdlib-identity-stubs: NOT OK.", file=sys.stderr)
    else:
        print("[+] stdlib-identity-stubs: OK — %d known stub(s), none new; %d still "
              "UNADJUDICATED (ceiling %d)." % (len(baseline), len(unadj),
                                               MAX_UNADJUDICATED))
    return rc


if __name__ == "__main__":
    sys.exit(main())
