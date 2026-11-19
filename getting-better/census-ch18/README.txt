ch18 re-drain census @00d6635b (after routes #235-#253). Base loop, gen #36.

METHOD. For each of the 429 live `#@ \trusted` markers (getting-better/trusted-reasons.tsv; the
grep metric reads 457), in a scratch copy of the tree: port the live body verbatim
(bin/port-one-mirror-body.py --convert --replace), copy the live signature, emit --no-proof
(heavy.sh QUICK), record the first blocker, restore. census.tsv holds one row per marker.

RESULT: 381 FAIL, 24 NOPORT (mixin-duplicate defs with no live twin), 24 TCOK.
Top first blockers among the FAILs: in-place mutators 55 (.pop 18, .setdefault 12, .extend 8,
.update 6, .add 5, other 6); erased value flowing into a builtin slot (#252) 39; nested-closure
lift 22; int/string/array/record value-model type errors 171; dict/set alias rule (#243) 6;
`except ... as e` reads (#233) 4; array-local reassignment 3; heterogeneous lists 5;
`with ... as` 9; name rebinding 8; tuple-pattern loops 4; higher-order args 5;
L3-tc SYNTAX errors 4 (see below).

THE 24 TCOK: NOT ONE IS A HONEST CONVERSION.
  CHECK 0, trusted parent (7): Module6 _sig_val_from_let._hdr_name, _transpile_modular._emit_funcs;
    pycsl _run_vacuity_gate._probe_one(+._is_false_goal), _dispatch_provers._finalize,
    _run_proofs._gate_vacuity_then_succeed; core_ir_semantic _returns_literal_none.walk.
  INPUT-BLIND per bin/check-emitted-vacuity.py (5): identifiers.stable_hash,
    monomorphize._rewrite_call_sites, Module3_Weaver._attach_loop_contracts,
    pure_ast _Parser.error, _Parser.unsupported.
  EMISSION-INERT (2): statements _collect_string_elem_read_locals.rec,
    _collect_field_decode_str_locals.rec -- the parent is a GenericFold recognizer; dropping the
    nested marker leaves the .mlw byte-identical, so the conversion would relabel, not prove.
  YIELD-ERASED generators (3): sertop._sexp_tokens, pure_ast.iter_fields, iter_child_nodes
    (every `yield` lowers to `let _ = any int in ()`; the output is not modelled).
  ERASED FACADES (5): ir_schema.validate_ir (0-ary `func_keys_0 ()`, set minus as int `-`),
    pycsl._parse_args (receiver-erased argparse ops on hashed literals),
    pure_ast _Parser._max_end (`cur := any int`, recursion via an abstract op),
    _parse_number (`int(s)` lowered to `s`), NodeVisitor.generic_visit (`value = any int`).
  DO-NOT-CONVERT (1): audit_proof_reverify._cache_root (mkdir effect, `assigns \nothing`).
  SOUNDNESS-BLOCKED (1): pure_ast _Unparser.visit_If -- `with self.block():` is dropped (the
    bare-`with` hole below).

SOUNDNESS BUG FOUND (not fixed; reproducers in repro/). A BARE `with <cm>:` (no `as`) is lowered
by Module5 `_py_stmt_with` to its body alone: __enter__/__exit__ never run. The ROUTE #38/#39 guard
refuses this only when THE SAME FILE defines a context-manager CLASS. Two carriers escape it:
  repro/xmod/w2524_bare_with_imported_cm.py  -- the CM class is IMPORTED (cmlib.py).
      `#@ ensures \result == 0`, CPython returns 1: rc=0 "All contracts formally proven".
      True twin w2525 (`== 1`) FAILS. Run with --import-path repro/xmod.
  repro/w2526_bare_with_contextmanager_method_framed.py -- an in-file @contextmanager METHOD
      whose body writes self.n (`#@ assigns self.n`). Same false claim: rc=0. True twin w2527 FAILS.
  Controls: w2520 (in-file CM class, enter effect) and w2521 (in-file suppressing __exit__) are
  REFUSED by #38/#39, as designed.

EMITTER BUG (fail-closed): a for-loop over a call with an erased argument puts `(any int)` inside
`variant { ... }` -- a program construct in a logic term -> WhyML syntax error
(monomorphize._collect_instantiations; also _ContractParser._parse_contract, _parse_atom_name,
pure_ast.unparse fail L3-tc with "syntax error").
