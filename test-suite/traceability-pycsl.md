# PyCSL Annotation Traceability Matrix

Each row corresponds to a numbered item in `annotations.md`.
The **Ref** column uses the format `section.subsection.row`.

| Ref | Section Title | Tested By | Status |
|-----|---------------|-----------|--------|
| 2.1.1 | Precondition \| `#@ requires <expr>` \| Function/method \| Must hold at entry | 0001, 0066, 0067 | PASS |
| 2.1.2 | Postcondition \| `#@ ensures <expr>` \| Function/method \| Must hold at exit | 0002, 0068, 0069 | PASS |
| 2.1.3 | Frame condition \| `#@ assigns <targets>` \| Function/method \| Only listed targets may be mutated | 0003, 0070, 0071 | PASS |
| 2.2.1 | Loop invariant \| `#@ loop invariant <expr>` \| `while`/`for` \| Inductive property preserved each iteration | 0004, 0072, 0073 | PASS |
| 2.2.2 | Loop variant \| `#@ loop variant <expr>` \| `while`/`for` \| Termination measure (must decrease, stay ≥ 0) | 0005, 0074, 0075 | PASS |
| 2.3.1 | Class invariant \| `#@ class invariant <expr>` \| `class` \| Must hold at every method boundary | 0006, 0076, 0077, 0191, 0192, 0193 | PASS |
| 2.4.1 | Label \| `#@ label <NAME>` \| Statement \| Marks a program point for `\at` references | 0007, 0078, 0079 | PASS |
| 2.4.2 | Ghost assign \| `#@ ghost <name> = <expr>` \| Statement \| Declare/assign ghost variable | 0207, 0208, 0209 | PASS |
| 2.4.3 | Ghost augmented assign \| `#@ ghost <name> += <expr>` \| Statement \| Augmented assign ghost variable | 0207, 0208, 0209 | PASS |
| 3.1.1 | `42`, `-1`, `0` \| `Number` \| Integer literal | 0008, 0080, 0081 | PASS |
| 3.1.2 | `x`, `n`, `total` \| `Var` \| Variable reference | 0009, 0082, 0083 | PASS |
| 3.1.3 | `self.field` \| `FieldAccess` \| Class field access | 0010 | UNPROVEN |
| 3.1.4 | `arr[i]` \| `SubscriptAccess` \| Array element access | 0011, 0084, 0085 | PASS |
| 3.1.5 | `\result` \| `Result` \| Return value (only in `ensures`) | 0012, 0086, 0087 | PASS |
| 3.1.6 | `\old(<expr>)` \| `Old` \| Value of expression at function entry | 0013, 0088, 0089 | PASS |
| 3.1.7 | `\at(<expr>, L)` \| `At` \| Value of expression at label `L` | 0014, 0090, 0091 | PASS |
| 3.1.8 | `\length(arr)` \| `ArrayLength` \| Length of array `arr` | 0015, 0092, 0093 | PASS |
| 3.1.9 | `\valid(arr, n)` \| `Valid` \| `arr[0..n)` is allocated | 0016, 0094, 0095 | PASS |
| 3.1.10 | `\separated(a, na, b, nb)` \| `Separated` \| Regions `a[0..na)` and `b[0..nb)` don't overlap | 0017, 0096, 0097 | PASS |
| 3.1.11 | `\length2d(a, m, n)` \| `Length2D` \| `a` has `m` rows each of length `n` | 0018 | FAIL |
| 3.1.12 | `\valid2d(a, i, j)` \| `Valid2D` \| `(i,j)` is a valid 2D index | 0019 | FAIL |
| 3.1.13 | `\nothing` \| `Nothing` \| Empty assigns target (pure function) | 0020, 0098, 0099 | PASS |
| 3.1.14 | `"hello"` \| `StringLiteral` \| String literal (uses Why3 `string.String`) | 0188, 0189, 0190 | PASS |
| 3.2.1 | 1 (lowest) \| `\forall var; body`, `\exists var; body` \| `Forall`, `Exists` \| Quantifiers (no direct equivalent) | 0021, 0100, 0101 | PASS |
| 3.2.2 | 2 \| `==>` (implies), `<==>` (iff) \| `BinOp` \| `not a or b`, `a == b` | 0022, 0102, 0103 | PASS |
| 3.2.3 | 3 \| `or` \| `BinOp` \| `or` | 0023, 0104, 0105 | PASS |
| 3.2.4 | 4 \| `and` \| `BinOp` \| `and` | 0024, 0106, 0107 | PASS |
| 3.2.5 | 5 \| `==`, `!=` \| `BinOp` \| `==`, `!=` | 0025, 0108, 0109 | PASS |
| 3.2.6 | 6 \| `<`, `>`, `<=`, `>=` \| `BinOp` \| same | 0026, 0110, 0111 | PASS |
| 3.2.7 | 7 \| `+`, `-` \| `BinOp` \| same | 0027, 0112, 0113 | PASS |
| 3.2.8 | 8 \| `*`, `/` \| `BinOp` \| same | 0028, 0114, 0115 | PASS |
| 3.2.9 | 9 (highest) \| `not`, unary `-`, unary `+` \| `UnaryOp` \| same | 0029, 0116, 0117 | PASS |
| 3.4.1 | `\nothing` \| No mutation allowed | 0030, 0118, 0119 | PASS |
| 3.4.2 | `x` \| Variable `x` may be mutated | 0031, 0120, 0121 | PASS |
| 3.4.3 | `x, y` \| Variables `x` and `y` may be mutated | 0032, 0122, 0123 | PASS |
| 3.4.4 | `self.field` \| Field may be mutated | 0033, 0124, 0125 | PASS |
| 3.4.5 | `arr[lo..hi]` \| Array region `arr[lo..hi)` may be mutated | 0034, 0126, 0127 | PASS |
| 4.1 | `//` (floor division) \| No grammar rule | 0035, 0128, 0129 | PASS |
| 4.2 | `%` (modulo) \| No grammar rule (WhyML has `mod` but not mapped from `%`) | 0036, 0130, 0131 | PASS |
| 4.3 | `len(...)` \| Use `\length(arr)` instead | 0037, 0132, 0133 | PASS |
| 4.4 | Function calls \| Contracts are pure logical expressions | 0038, 0134, 0135 | PASS |
| 4.5 | String literals \| Not in grammar | 0039, 0136, 0137 | PASS |
| 4.6 | `True` / `False` / `None` \| Use `1 == 1` / `1 == 0` / not applicable | 0040, 0138, 0139 | PASS |
| 4.7 | `in`, `not in` \| Not in grammar | 0041, 0140, 0141 | PASS |
| 4.8 | List comprehensions \| Not in grammar | 0042, 0142, 0143 | PASS |
| 4.9 | `if`/`else` ternary \| Not in grammar | 0043, 0144, 0145 | PASS |
| 5.1 | Hoare (default) \| `--memory-model hoare` \| Value-typed (`array int`) \| Not modeled (independent) | 0044, 0146, 0147 | PASS |
| 5.2 | Typed \| `--memory-model typed` \| Heap-based (`map loc int`) \| `\separated` needed | 0045, 0148, 0149 | PASS |
| 5.3 | Store \| `--memory-model store` \| Single untyped heap \| `\separated` needed | 0046, 0150, 0151 | PASS |
| 9.1 | `0` \| All goals verified (Valid) | 0047, 0152, 0153 | PASS |
| 9.2 | `1` \| Verification failed, incomplete, or pipeline error | 0048, 0154, 0155 | PASS |
| 2.1.4 | Function variant \| `#@ \variant <expr>` \| Termination measure for recursive functions | 0049, 0156, 0157 | PASS |
| 2.1.5 | Structural variant \| `#@ \variant (<expr>, <ordering>)` \| Well-founded ordering | 0050 | UNSUPPORTED |
| 2.1.6 | Diverges \| `#@ \diverges` \| Function may not terminate | 0051, 0158, 0159 | PASS |
| 2.1.7a | Trusted (correct body) \| `#@ \trusted` \| Body not verified, contracts assumed | 0052, 0160, 0161 | PASS |
| 2.1.7b | Trusted (wrong body) \| `#@ \trusted` \| Caller still proven from assumed contracts | 0053, 0162, 0163 | PASS |
| 9.3 | `--fun` with dependency tracking \| Only named function and transitive callees verified | 0054, 0164, 0165 | PASS |
| 9.4 | `--fun` single function \| Only named function verified, others trusted | 0055, 0166, 0167 | PASS |
| 9.5 | Multi-file `from mod import name` \| Imported function auto-resolved as trusted stub | 0056, 0168, 0169 | PASS |
| 9.6 | Multi-file `from mod import a, b` \| Multiple imports resolved from same module | 0057, 0170, 0171 | PASS |
| 9.7 | External module import \| Unresolved external import skipped, no crash | 0058, 0172, 0173 | PASS |
| 9.8 | Multi-file `import mod as alias` \| Module-qualified calls resolved via alias | 0059, 0174, 0175 | PASS |
| 9.9 | Multi-file `from mod import name as alias` \| Aliased import resolved and renamed | 0060, 0176, 0177 | PASS |
| 9.10 | Multi-file relative import \| `from .mod import name` resolved relative to file | 0061, 0178, 0179 | PASS |
| 9.11 | Multi-file `import mod` (bare) \| Dotted calls resolved via full module path | 0062, 0180, 0181 | PASS |
| 9.12 | Multi-file `from mod import *` \| Wildcard import, only called functions resolved | 0063, 0182, 0183 | PASS |
| 9.13 | Multi-file `--deep` transitive chain \| A→B→C imports recursively resolved | 0064, 0184, 0185 | PASS |
| 9.14 | Multi-file circular import detection \| Circular imports detected with --deep, no crash | 0065, 0186, 0187 | PASS |
| 4.1 | Pure functions in contracts \| `func(args)` in `requires`/`ensures` \| Functions with `assigns \nothing` usable in specs | 0194, 0195, 0196 | PASS |
| 1.1 | Data structure contract atoms \| `\is_sorted`, `\sum`, `dict` type | 0197, 0198, 0199 | PASS |
| 2.1 | Division-by-zero guards \| `//` and `%` in program code generate proof obligations | 0200 | PASS |
| 2.1.8 | Bounded integers \| `#@ assumes bounded_int(N)` \| Overflow VCs on arithmetic | 0202, 0203, 0204 | PASS |
| 2.1.9a | Raise statement \| `raise ExcType` in body \| Auto-declares exception, adds `raises` clause | 0205 | PASS |
| 2.1.9b | Raises contract \| `#@ raises ExcType when <cond>` \| Exceptional postcondition | 0206 | PASS |
| 7.1 | Assert statement \| `assert cond, "msg"` \| Emits `check { [@expl:msg] cond }` in WhyML | 0221, 0222, 0223 | PASS |
| 3.2.8 | Floor div and modulo in contracts \| `//`, `%` in `requires`/`ensures` \| Maps to `div`/`mod` | 0224, 0225, 0226 | PASS |
| 3.1.18 | Boolean literals in contracts \| `True`, `False` \| `CSLBool` atom | 0227, 0228, 0343, 0344 | PASS |
| 3.1.19 | None literal in contracts \| `None` \| `CSLNone` atom (maps to 0) | 0229 | PASS |
| 3.2.6b | Membership operators in contracts \| `in`, `not in` \| Desugared to `∃` quantifier | 0230, 0231, 0232 | PASS |
| — | Library stubs \| `functools`, `itertools` trusted stubs | 0233 | PASS |
| 7.3 | Walrus operator \| `(x := expr)` in body \| Named expression with side-effect | 0234, 0235 | PASS |
| 3.1.20 | Slice notation \| `arr[lo:hi]` in contracts and body \| Abstract `array_slice` | 0236, 0237 | PASS |
| 7.2 | Tuple unpacking \| `a, b = expr` \| Destructuring assignment | 0238, 0239, 0352 (Euclidean GCD loop body) | PASS |
| 7.4 | Match statement \| `match/case` \| Lowered to if/elif chain | 0240, 0241 | PASS |
| 7.5 | Lambda expression \| `lambda params: body` \| Anonymous function | 0242, 0243 | PASS |
| 2.1.10 | Thread entry \| `#@ thread_entry` \| Marks function as concurrent thread entry point | 0250, 0251, 0252, 0253, 0277 | PASS |
| 2.4.4 | Critical section \| `#@ critical <mutex>` \| with-block is a critical section (havoc+assume+assert) | 0250, 0251, 0252, 0253, 0278; XFAIL: 0254 (unprotected write) | PASS |
| 2.4.5 | Acquires \| `#@ acquires <mutex>` \| Explicit mutex acquire annotation | 0262, 0263, 0264, 0265, 0266; XFAIL: 0255 (missing lock_order) | PASS |
| 2.4.6 | Releases \| `#@ releases <mutex>` \| Explicit mutex release annotation | 0267, 0268, 0269, 0270, 0271 | PASS |
| 2.5.1 | HAPPY (region) \| `#@ happy <name>: region LO..HI writes self.<field> outside region` \| Per-site disjointness check | 0459, 0460 | PASS |
| 2.5.2 | Preserves \| `#@ \preserves` \| Trusted/abstract HAPPY trust-boundary opt-in | 0461; XFAIL: 0462 | PASS |
| 2.5.3 | HAPPY (protects) \| `#@ happy <name>: protects <paths> [except …]` \| Subsystem ownership; per-site `check False`; aliasing rejected (07-1143 R1/R2) | 0611; XFAIL: 0612, 0613 | PASS |
| 2.5.4 | HAPPY (parametric) \| `#@ happy <name>(p): protects <path>[LO:HI]` \| Per-object containment check (07-1143 R3) | 0614; XFAIL: 0615 | PASS |
| 2.5.5 | Footprint \| `#@ footprint <name>(arg)` \| Binds a parametric HAPPY's parameter (07-1143 R3) | 0614; XFAIL: 0615 | PASS |
| 5.4 | Concurrent memory model \| `--memory-model concurrent` \| Monitor-invariant sequential reduction | 0250, 0251, 0252, 0253, 0277 | PASS |
| 10.1.1 | Protected shared variable \| `#@ shared <var> protected_by <mutex>` \| Shared global with mutex | 0250, 0251, 0252, 0253, 0280 | PASS |
| 10.1.2 | Unprotected shared variable \| `#@ shared <var>` \| Shared global without mutex (lenient) | 0272, 0273, 0274, 0275, 0276 | PASS |
| 10.1.3 | Mutex invariant \| `#@ mutex_invariant <mutex>: <expr>` \| Invariant held when mutex free | 0250, 0251, 0252, 0253, 0279; XFAIL: 0256 (violated invariant) | PASS |
| 10.1.4 | Lock order \| `#@ lock_order <m1>, <m2>, ...` \| Total order on mutex acquisition | 0257, 0258, 0259, 0260, 0261; XFAIL: 0255 (missing lock_order) | PASS |
| E1 | Negative: `\result` in non-ensures context \| Must be rejected by Module4 | XFAIL: 0281 (requires), 0282 (loop invariant) | PASS |
| E2 | Negative: undefined variable in contract \| Must be rejected by Module4 | XFAIL: 0283 (ensures) | PASS |
| E5 | Negative: bare variable in class invariant \| Must be rejected by Module4 | XFAIL: 0284 (undeclared), 0285 (not a field) | PASS |
| 11.1.2 | Ghost string variable \| `#@ ghost s : string = "..."` \| `ref string` in WhyML, `^` for concat | 0292 | PASS |
| 11.1.3 | Ghost array variable \| `#@ ghost snap : array = \copy(arr)` \| `array int` snapshot | 0293 | PASS |
| 11.1.4 | Ghost dict variable \| `#@ ghost d : ghost_dict = \empty_map` \| `ref (map int (option int))` | 0294 | PASS |
| 11.1.5 | Ghost list variable \| `#@ ghost l : ghost_list = \nil` \| `ref (list int)` | 0295 | PASS |
| 11.1.6 | Ghost set variable \| `#@ ghost s : ghost_set = \set_empty` \| `ref (map int bool)` | 0296 | PASS |
| 11.1.7 | Ghost tuple variables \| `#@ ghost p : tuple2 = \mktuple(a, b)` \| `ref (int, int)` | 0297 | PASS |
| 11.2.3 | Ghost string `\str_length`/`\str_sub` \| `\str_length(s)`, `\str_sub(s, lo, hi)` \| `String.length`, `String.sub` | 0298 | PASS |
| 11.2.9 | Ghost list `+=` shorthand \| `#@ ghost l += x` \| prepend via `Cons x !l` | 0300 | PASS |
| 11.2.5 | Ghost dict `+=` shorthand \| `#@ ghost d += \mktuple(k, v)` \| `Map.set !d k v` | 0300 | PASS |
| 11.2.6 | Ghost set union/inter/diff \| `\set_union`, `\set_inter`, `\set_diff` \| functional set ops | 0299 | PASS |
| 11.2.11 | Ghost set `+=` shorthand \| `#@ ghost s += x` \| `Map.set !s x true` | 0301 | PASS |
| 11.4.1 | Negative: `\proj` dynamic index \| `\proj(t, n)` where `n` is not a literal | 0302 | XFAIL |
| 11.4.2 | Negative: `\proj` arity mismatch \| `\proj(p, 2)` on `tuple2` (Why3 error) | 0303 | XFAIL |
| 11.4.3 | Negative: ghost string `+=` \| `#@ ghost s += expr` rejected at Module4 | 0304 | XFAIL |
| 11.1.1 | Ghost tuple2 end-to-end proof \| `\fst`/`\snd` in loop invariant, proven by Alt-Ergo | 0305 | PASS |
| 11.3.1 | Ghost list length proof \| `\list_length(l) == i` loop invariant, proven by Alt-Ergo | 0306 | PASS |
| 11.2.6b | Ghost dict `\map_eq` in loop invariant \| two synchronized dicts | 0307 | PASS |
| 11.2.7 | Ghost set `\set_union` with `\set_mem` \| `\set_mem(k, \set_union(s1, s2))` | 0308 | PASS |
| 11.1.2b | Ghost tuple3 proof \| `\proj(t, i)` in loop invariant, proven by Alt-Ergo | 0309 | PASS |
| 11.2.4b | Ghost dict `Map.get`/`Map.set` proof \| `\map_get(d, 0) == i` loop invariant | 0310 | PASS |
| 11.2.6c | Ghost dict `\map_eq` full proof \| `\map_eq(d1, d2)` with synchronized updates | 0311 | PASS |
| 11.3.2 | Ghost list `\nth` proof \| `\nth(log, 0) == i - 1` head tracking, `list.NthNoOpt` | 0312 | PASS |
| 7.2.1 | Ghost array `\make` + `ghost snap[i] = e` proof \| element update with bounds check | 0313 | PASS |
| 11.3.3 | Ghost list `\mem` proof via `axiom mem_head` \| `\mem(i-1, log)` with soundness axiom | 0314 | PASS |
| 7.2.2 | Ghost array `\copy` element preservation \| `snap[i-1] == arr[i-1]` after `\copy(arr)` | 0315 | PASS |
| 11.5 | Multi-ghost-type: dict + list + set \| three ghost types in same function, proven by Alt-Ergo | 0316 | PASS |
| 11.4.1b | Negative: `\proj` dynamic index rejected (XFAIL) \| `\proj(t, i)` where `i` is a loop variable | 0317 | XFAIL |
| 11.3.4 | Ghost list `\list_length` proof \| `\list_length(log) == i` loop invariant | 0318 | PASS |
| 11.1.4 | Ghost tuple4 proof \| `\proj(t, 0..3)` all four components, proven by Alt-Ergo | 0319 | PASS |
| 11.2.4c | Ghost dict `\has_key` proof \| `\has_key(d, 0)` option-type: key present | 0320 | PASS |
| 11.4.3b | Ghost string `^` concat proof \| `\str_length(s) == i` with `s ^ "x"` update | 0321 | PASS |
| 11.3.5 | Ghost list `\append` + `\list_length` proof \| `\list_length(\append(a, b)) == i` | 0322 | PASS |
| 11.2.8 | Ghost set `\set_eq` proof \| `\set_eq(s1, s2)` synchronized updates, proven by Alt-Ergo | 0323 | PASS |
| 11.2.4d | Ghost dict `\has_key` with key=1 \| `\has_key(d, 1)` implication invariant | 0324 | PASS |
| 11.2.3b | Ghost set `\set_card` bounded range proof \| `\set_card(s, 0, i) == i` loop invariant | 0325 | PASS |
| 11.5.1 | Ghost trailing-block position \| ghost update as last line in loop body, emitted after last statement | 0326 | PASS |
| 11.6.1 | Ghost array \\copy_range bounded snapshot \| \\copy_range(arr, 0, n) with forall invariant, proven by Alt-Ergo | 0327 | PASS |
| 11.7.1 | Memory-model parity for \\copy_range \| ghost array snapshot in hoare model with explicit --memory-model hoare flag | 0328 | PASS |
| 11.8.1 | Ghost string \\str_sub prefix length proof \| `\str_length(\str_sub(s, 0, i)) == i` loop invariant, proven by Alt-Ergo (all 8 sub-goals) | 0329 | PASS |
| 11.9.1 | Ghost dict \\map_remove + option-type proof \| `\has_key(d, 1)` true when stored value is 0 (option-type fix), \\map_remove verified | 0330 | PASS |
| 12.1.1 | Body dict modelling — round-trip read \| `d = {}; d[k] = v; return d[k]` lowers to `ref (const (None: option int))` + `map_update_some` + `Map.get` | 0345 | PASS |
| 12.1.2 | Body dict membership \| `k in d` / `k not in d` lowers to `match Map.get` (option `Some`/`None`) | 0346 | PASS |
| 12.2.1 | Body set modelling \| `set()` + `s.add(x)` + `x in s` shares the dict's `map int (option int)` model; `.add`/`.discard` use `map_update_some`/`map_update_none` wrappers | 0347 | PASS |
| 12.3.1 | Multi-argument `range(start, stop)` under full proof \| Loop with `for i in range(s, e)`, sum accumulator + invariants | 0348 | PASS |
| 12.4.1 | `Optional[T]` return annotation \| Module5 unwraps `Optional[T]` to T (since `None` maps to `0`) | 0349 | PASS |
| 12.4.2 | `Union[T, None]` return annotation \| Module5 heuristic picks the first non-`None` component | 0350 | PASS |
| 12.5.1 | `sorted` builtin on array \| Emits abstract `val sorted_1 (a: array int) : array int`; target tracked as array-typed | 0351 | PASS |
| 12.5.2 | `bytes()`/`bytearray()` constructors \| Faithful `array int` constructor — length- and element-preserving `ensures` (empty → length 0); result tracked as array-typed (07-1321 S1) | 0616 | PASS |
| 12.5.3 | array-ref local deref at call site \| Ref-wrapped array local passed to a callee is dereferenced (`!x`); plain args unchanged (07-1321 S2) | 0617 | PASS |
| 12.5.4 | `b'\x00' * N` byte-literal repetition \| Lowers to `array int` (`Array.make N 0`), incl. slice-assignment RHS (`Array.blit`) (07-1321 S3) | 0618 | PASS |
| 12.5.5 | `array += array` concatenation \| List/bytes `+=` target recognised as array-typed → `array_extend` (deref'd), not integer `+`; faithful length-additive concat is a follow-on (07-1321 S4) | 0619 | PASS |
| 12.6.1 | quantify over list element / range \| `\forall x in a;` (membership) and `\forall i in range(lo,hi);` → direct `lo<=i<hi` bound (07-1311 Q1) | 0620; XFAIL: 0622 | PASS |
| 12.6.2 | quantify over dict keys / values \| `\forall k in d;` / `d.keys()` → `Map.get d k <> None`; `\forall v in d.values();` → `exists k. Map.get d k = Some v` (07-1311 Q2/Q3) | 0621 | PASS |
| 12.6.3 | collection-typed binder \| `\forall a : list;` (`array int`) / `\forall m : dict;` (`map int (option int)`); `m[k]` is a map lookup (07-1311 Q4) | 0623; XFAIL: 0625 | PASS |
| 12.6.4 | two-binder dict items \| `\forall k, v in d.items();` → `forall k. match Map.get d k with Some v -> P | None -> true end` (07-1311 Q3) | 0624 | PASS |
| 12.7.1 | seq-promotion analysis \| a list local/param GROWN (`+=` list RHS / `a+b`) is marked seq-modelled; int accumulators not promoted (07-1705-rev4 P2) | (metadata; exercised via 12.7.2) | PASS |
| 12.7.2 | growable list local (seq model) \| a grown list LOCAL is `ref (seq int)`: init `Seq.cons` chain, `+=`→`!a ++ snapshot(b)`, `len`→`Seq.length`, `a[i]`→`Seq.get`; proves the length-additive law + element placement (07-1705-rev4 P3) | 0626, 0627, 0628 | PASS |
| 12.7.3 | seq return boundary \| `return a` of a seq local → `materialize !a` (fresh array); build-by-concat then return proves `\length(\result)` (07-1705-rev4 P4) | 0629 | PASS |
| 12.7.4 | growable list PARAM (seq model) \| a grown list param is shadowed `let a = ref (snapshot a)`; concat + `return` materialise prove `\length(\result) == \length(a)+\length(b)`; `array_extend` removed (07-1705-rev4 P5) | 0619 | PASS |

## NoException + UB Detection (workplan PRs 1–10, 2026)

| Block | Tests | Coverage | Status |
|---|---|---|---|
| no_exception.parser       | 0353–0357 | Parser support + rejection cases | PASS |
| no_exception.preamble     | 0358      | WhyML predicate vocabulary | PASS |
| no_exception.vc-injection | 0359–0380 | VC injection for div/mod/index/key | PASS |
| no_exception.interproc    | 0381–0386 | Inter-procedural propagation | PASS |
| no_exception.all-form     | 0391–0393 | `\all` wildcard form | PASS |
| ub.c-extension            | 0396–0400 | ctypes/cffi deny-list | PASS |
| ub.finalizer              | 0401–0403 | `__del__` rejection | PASS |
| ub.iteration-mutation     | 0404–0407 | Mutating iterated container | PASS |
| ub.hash-eq                | 0411–0414 | Hash/eq consistency | PASS |
| ub.concurrent-strict      | 0415–0417 | `--strict-concurrent-checks` | PASS |

## Self-annotation suite (2026-05-28)

Modules from `src/pycsl/` mirrored under `src/self-annotate/src/` with
`#@` contracts; each mirror passes `pycsl <file>` with full Why3 proof.
26 modules total (see `bin/run-self-annotation-suite.sh` for the
canonical list).

| Bucket | Modules | Annotation kind |
|---|---|---|
| A — full proof tractable | errors, ir_schema, exception_model, 6× module6_whyml data+logic mixins, 2× __init__ | `\trusted reviewer:` stubs (interface contracts; bodies stubbed) |
| B — needs richer stubs | import_classifier, ConcurrencyChecker | `\trusted reviewer:` stubs |
| C — research-grade | Module{1–6}, audit_proof, pycsl.py CLI, 4× module6_whyml heavy mixins | `\trusted reviewer:` stubs; future PRs cite formal-semantics theorems |

**Anti-drift gate:** `bin/self-annotate-mirror-check.sh` verifies every
mirror's function and class signatures match its `src/pycsl/`
counterpart. Drift triggers a hard fail with the actionable diff.

**Re-generation:** `bin/self-annotate-stub-gen.py src/pycsl/<file>
src/self-annotate/src/<file>` rebuilds a mirror from current source.
