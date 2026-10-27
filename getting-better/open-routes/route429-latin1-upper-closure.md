# OPEN ROUTE #429 — str.upper() OF A LATIN-1 STRING CAN LEAVE LATIN-1; THE MODEL KEEPS EVERY CODE POINT < 256 
**Status: OPEN, Severity 2 (arguable).** Red-team round 33 (2026-10-27, convergence measurement after the run #3 allow-list repairs; 653 screened / 385 fully proved / 116 confirmed); driver-reproduced on main (see `scratchpad/rt33/driver-repro.txt`).
Witnesses `witnesses-r429/` (2): `p03_upper_ydiaeresis.py`, `p04_upper_micro.py`.

```
#429 str.upper() OF A LATIN-1 STRING CAN LEAVE LATIN-1; THE MODEL KEEPS EVERY CODE POINT < 256   [arguable: LATIN1-STR closure]  (2)
  p03  ensures ord(s.upper()[0]) < 256, s = "ÿ" PROVED                                       CPython 376 (U+0178)
  p04  s = "µ" (micro sign)                                                                  CPython 924 (U+039C)
  The INPUT is inside LATIN1-STR's domain; the result of a str method is not, while the model asserts it is. (Length changes
  -- "ß".upper() / casefold / title / capitalize / swapcase -- FAIL, so the model does not claim length preservation.)
  REPAIR: either restrict LATIN1-STR's "every str" to exclude results of upper/title/capitalize/swapcase/casefold, or give
  these methods no code-point-range postcondition.

DECLARED MODEL ASSUMPTIONS / HELD ROUTES MEASURED LIVE (PROVED, NOT counted)
  x_a16 BUILTIN-EXACT; x_i17 FLOAT-FINITE; x_g03 / x_g04 / x_h07 / x_j22 / x_j26 route #411 (held; still PROVE at bcefbe788).

CORRECTLY REFUSED / FAILED (selection of what attacked the new rules head-on)
  #404 metaclass: ABCMeta / EnumMeta / builtins.type / `T = type` bases, an inherited metaclass M2(M), metaclass= via **KW,
       __init_subclass__ / class decorator / __set_name__ stores, type.__setattr__(M, "__hash__", ..) at module level or in
       the driver, setattr(*(..)) (a01-a12, s01-s04): refused.
  #403 / #402: unverified __eq__ / __ne__ / __lt__ / __gt__ / __bool__ / __len__ / __str__ / __format__ / __repr__ / __iter__
       / __contains__ / __index__ / __enter__ raising under no_exception (h20-h39): refused or failed.
  #226 flip: subclass __init__ breaking the invariant, module-function store, setattr, property setter, custom __setattr__,
       default-param violation, mutating method, class-attribute shadow, dataclass, list-param alias, fill alias, keyword
       super(): refused / failed (d01-d18). Explicit dynamic stores (__setattr__, object.__setattr__, __dict__, vars): n02-n06 failed.
  #412-#417: pow(0, -1), divmod(a, 0), x ** -1.0, mixed int/float overflow, slice step 0, bytes(10**20), ljust / zfill /
       center huge, to_bytes, chr, str/list.index, remove, pop, popitem, next, max/min empty, pow(.., .., 0), shifts by a
       negative count, range length with a step, str repetition (e01-e70): refused or failed. `%` with trailing '%', '%%'
       width, huge width / precision, %d past 4300 digits (k01-k30): refused or failed.
  #420: shapes with ensures / no_exception now go generic (r01-r06, o00-o06): refused, ill-typed or failed.
  Shared mutable state: mutable default args, class-attribute list, iterator exhaustion, closures, lru_cache, [row] * 2,
  dict.fromkeys / setdefault / get aliasing (p30-p39): refused or failed. Module-level / driver mutation of a global after
  its definition (m30-m43): refused or failed.
  Unicode: ß length changes, isalpha / isupper / isidentifier / isprintable / strip / split / splitlines on Latin-1
  whitespace and letters, isdigit '²' then int(): failed (p01-p23 except p03 / p04).

NOTES
  Further families tried after the first write-up, all REFUSED or FAILED (no false proof):
  u00-u23  stdlib / unbound-method mutation of a list / dict / set / bytearray argument (heapq, bisect, operator.setitem /
           iadd / delitem, list.append(xs, ..), dict.update(d, ..), struct.pack_into, map / reduce / sort-key side effects,
           genexp exhaustion, a generator function over the mutated dict): the frame is havocked or the call refused.
  v01-v35  hashing through lru_cache / Counter / dict.fromkeys / set().union / frozenset / dict(zip) of List[List[int]];
           json.dumps of unserializable values; the §7.83 listed stdlib functions with bad arguments (shlex.quote(int),
           os.path.join mixes, math domain / range errors, randint, unicodedata, textwrap widths): refused or failed.
  y00-y06  a subclass that becomes unhashable (own __eq__, @dataclass, __eq__ = A.__eq__, __hash__ = None, grandchild).
  z00-z14  subclasses / metaclasses defined in a nested class body or under if / try / with / for / while (closed world
           holds for every statement nesting), GD and override refinement through them.
  q00-q19  int -> float OverflowError in **0.5, pow, sum, math.isfinite / isinf / isnan / isclose / fabs / hypot / atan2 /
           sin / fsum / pow / exp, complex(n), divmod(n, 1.0), round(n * 1.0), random.uniform; time.sleep(-1).
  r00-r38  Python semantics of % and // with negative divisors (body and contract), divmod, str find / rfind / count /
           index / replace / split with empty needles, slices with negative steps, range lengths, round / int truncation,
           startswith(()), strip / lstrip / zfill / title / splitlines / split maxsplit / partition / min / < on str.
  xx01-18  raises-when narrowing, named no_exception sets vs subclasses (UnicodeDecodeError, JSONDecodeError,
           UnicodeEncodeError under ValueError; LookupError / ArithmeticError / Exception), finally-return, try/else,
           re-raise, handler raising, raise from, assert, contextlib.suppress, except tuples / bases.
  w00-w07  explicit / implicit dunder calls (__setitem__, __call__, __iadd__, A.put(a, ..), getattr(a, "put"), a bound
           method name) under a class invariant: all checked (only __init__ is the frame-less val, #425).
  f18 is an INVALID probe (the exception is raised by `f"{(2**40):c}"` in the driver). i-series first run used `-> object`
  (uninformative Unknown); re-run with `-> int` (the counted results). Timeouts are not counted (g01, j20, j21, j26, m16, p14-p16).
  Every pycsl run went through heavy.sh (<= 2 concurrent slots); no job of this team is left running.
```
