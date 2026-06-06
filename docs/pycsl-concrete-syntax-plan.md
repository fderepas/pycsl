# Plan: PyCSL Concrete Syntax Reference

**Goal:** Produce `docs/pycsl-concrete-syntax-reference.md` — the authoritative,
self-contained specification of PyCSL's concrete syntax using EBNF.

**Source of truth:** `test-suite/annotations.md` (paragraph numbering preserved).

---

## 1  Scope

The reference document will precisely define what strings constitute valid
PyCSL annotations. It covers:

- The embedding mechanism (how `#@` comments coexist with the Python parser)
- The complete EBNF grammar for every directive and expression form
- Lexical conventions (tokens, whitespace, escaping)
- Disambiguation rules and precedence
- Railroad diagrams for the main productions

The reference does NOT define what the annotations *mean* (static or
translational semantics) — only what sequences of characters are syntactically
valid.

---

## 2  Structure (mirrors `annotations.md` paragraph numbering)

### §1  Annotation Embedding Syntax

_Corresponds to annotations.md §1._

- Define the `#@` comment prefix
- Specify that annotations are single-line
- Specify the "leading lines" placement rule
- Formalize the `""  # pycsl` class-level anchor convention
- Specify interaction with Python's `#` comment syntax (no nesting)

**Deliverable:** Formal grammar for the physical annotation line:

```
annotation_line ::= INDENT? "#@" SP directive
```

### §2  Directives

_Corresponds to annotations.md §2._

For each directive row in annotations.md §2.1–§2.4, the reference will
provide:

| §    | Directive | Grammar production |
|------|-----------|-------------------|
| 2.1.1 | `requires` | `precondition ::= "requires" expr` |
| 2.1.2 | `ensures` | `postcondition ::= "ensures" expr` |
| 2.1.3 | `assigns` | `assigns ::= "assigns" assigns_target` |
| 2.1.4 | `\variant` (integer) | `function_variant ::= "\variant" expr` |
| 2.1.5 | `\variant` (structural) | `function_variant_structural ::= "\variant" "(" expr "," CNAME ")"` |
| 2.1.6 | `\diverges` | `diverges_decl ::= "\diverges"` |
| 2.1.7 | `\trusted` | `trusted_decl ::= "\trusted"` |
| 2.1.8 | `assumes bounded_int(N)` | `bounded_int_decl ::= "assumes" "bounded_int" "(" NUMBER ")"` |
| 2.1.9 | `raises` | `raises_decl ::= "raises" CNAME "when" expr` |
| 2.1.10 | `thread_entry` | `thread_entry_decl ::= "thread_entry"` |
| 2.2.1 | `loop invariant` | `loop_invariant ::= "loop" "invariant" expr` |
| 2.2.2 | `loop variant` | `loop_variant ::= "loop" "variant" expr` |
| 2.3.1 | `class invariant` | `class_invariant ::= "class" "invariant" expr` |
| 2.4.1 | `label` | `label_decl ::= "label" CNAME` |
| 2.4.2 | `ghost` (assign) | `ghost_assign ::= "ghost" CNAME "=" expr` |
| 2.4.3 | `ghost` (augmented) | `ghost_aug_assign ::= "ghost" CNAME AUG_OP expr` |
| 2.4.4 | `critical` | `critical_decl ::= "critical" mutex_expr` |
| 2.4.5 | `acquires` | `acquires_decl ::= "acquires" mutex_expr` |
| 2.4.6 | `releases` | `releases_decl ::= "releases" mutex_expr` |

### §3  Expression Language

_Corresponds to annotations.md §3._

#### §3.1  Atoms (20 rows)

For each atom in annotations.md §3.1:

| § | Syntax | Production |
|---|--------|-----------|
| 3.1.1 | Integer literal | `NUMBER` |
| 3.1.2 | Variable | `CNAME` |
| 3.1.3 | Field access | `"self" "." CNAME` |
| 3.1.4 | Subscript | `CNAME "[" expr "]"` |
| 3.1.4b | Chained subscript | `CNAME "[" expr "]" "[" expr "]"` |
| 3.1.5 | `\result` | `"\\result"` |
| 3.1.6 | `\old` | `"\\old" "(" expr ")"` |
| 3.1.7 | `\at` | `"\\at" "(" expr "," CNAME ")"` |
| 3.1.8 | `\length` | `"\\length" "(" CNAME ")"` |
| 3.1.9 | `\valid` | `"\\valid" "(" CNAME "," expr ")"` |
| 3.1.10 | `\separated` | `"\\separated" "(" CNAME "," expr "," CNAME "," expr ")"` |
| 3.1.11 | `\length2d` | `"\\length2d" "(" CNAME "," expr "," expr ")"` |
| 3.1.12 | `\valid2d` | `"\\valid2d" "(" CNAME "," expr "," expr ")"` |
| 3.1.13 | `\nothing` | `"\\nothing"` |
| 3.1.14 | String literal | `ESCAPED_STRING` |
| 3.1.15 | `\is_sorted` | `"\\is_sorted" "(" CNAME "," expr "," expr ")"` |
| 3.1.16 | `\sum` | `"\\sum" "(" CNAME "," expr "," expr ")"` |
| 3.1.17 | Function call | `CNAME "(" expr_list? ")"` |
| 3.1.18 | Boolean | `"True" \| "False"` |
| 3.1.19 | None | `"None"` |
| 3.1.20 | Slice | `CNAME "[" expr ":" expr "]"` |

#### §3.2  Operators (9 precedence levels)

For each operator row in annotations.md §3.2, the reference will provide:
- Formal precedence grammar (already expressed in the cascading `?expr` →
  `?implication` → `?logical_or` → … → `?atom` chain)
- Associativity (left for binary, right for implication)
- Token definitions

#### §3.3  Quantifiers

Formal grammar for `\forall` / `\exists` / `\exist` with greedy body parsing.

#### §3.4  Assigns targets

Formal grammar for assign target lists including `\nothing`, variables,
field access, and array regions `arr[lo..hi]`.

### §4  Unsupported Constructs

_Corresponds to annotations.md §4._

List constructs explicitly excluded from the grammar with rationale.

### §5  Memory Model Directives

_Corresponds to annotations.md §5._

Grammar for concurrent model directives: `shared`, `mutex_invariant`,
`lock_order`.

### §8  Complete EBNF

_Corresponds to annotations.md §8._

The full grammar reproduced as a single, self-contained EBNF specification.
This section is the normative grammar — all earlier sections are explanatory.

---

## 3  Methodology

1. **Extract** the current grammar from `Module2_Parser.py` (the Lark EBNF
   string inside `CSLParser.GRAMMAR`).
2. **Cross-reference** every production against annotations.md §1–§8.
3. **Identify gaps:** any directive or atom in annotations.md that lacks a
   corresponding grammar rule (or vice versa).
4. **Normalize** Lark syntax to standard EBNF (ISO 14977) for readability.
5. **Add railroad diagrams** for the 5 most commonly used productions
   (`precondition`, `postcondition`, `assigns`, `loop_invariant`, `expr`).
6. **Write** the reference document section by section.

---

## 4  Verification

- Every grammar rule must have at least one test file in
  `test-suite/corpus/pycsl-reference/` that exercises it.
- Cross-check against `test-suite/traceability-pycsl.md` for coverage.
- Run `Module2_Parser` on a battery of valid and invalid input strings
  to confirm the grammar accepts exactly what the reference specifies.

---

## 5  Estimated Effort

| Phase | Effort |
|-------|--------|
| Extract and normalize grammar | 2h |
| Write §1–§5 with examples | 4h |
| Write §8 (full EBNF) | 2h |
| Railroad diagrams | 1h |
| Cross-reference and gap analysis | 2h |
| **Total** | **~11h** |
