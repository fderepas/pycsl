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
| 2.3.1 | Class invariant \| `#@ class invariant <expr>` \| `class` \| Must hold at every method boundary | 0006, 0076, 0077 | PASS |
| 2.4.1 | Label \| `#@ label <NAME>` \| Statement \| Marks a program point for `\at` references | 0007, 0078, 0079 | PASS |
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
