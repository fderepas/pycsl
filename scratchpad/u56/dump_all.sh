#!/bin/bash
ROOT=/home/fabrice/git/pycsl-u56; cd "$ROOT" || exit 2
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
E=${EMIT:-$ROOT/scratchpad/u56/emit}; O=${OUTD:-$ROOT/scratchpad/u56/dump}
while read f fn; do
  [ -z "$f" ] && continue
  echo "=== $f $fn"
  PYTHONHASHSEED=0 timeout 600 .venv/bin/python3 -W ignore scratchpad/u56/probe_dump.py "$ROOT" "$E/$f.mlw" "$O/$fn" "$fn" 2>&1 | grep -v "^\[\*\]" | tail -8
done <<'L'
module6_whyml__statements statementemissionmixin___array_coerce_arg
module6_whyml__statements statementemissionmixin___first_assign_kind
module6_whyml__statements statementemissionmixin___wrap_body_with_return_catch
module6_whyml__stmt_control_flow controlflowstmtmixin___handle_if_stmt
module6_whyml__stmt_control_flow controlflowstmtmixin___handle_return_stmt
frontend__pure_ast _parser___looks_like_match
frontend__pure_ast _parser___sequence_pattern
frontend__pure_ast _parser___with_parenthesized
module6_whyml__expressions expressionemissionmixin___array_coerce_arg
module6_whyml__expressions expressionemissionmixin___coerce_to_int
module6_whyml__expressions expressionemissionmixin___dv_missing_default
module6_whyml__expressions expressionemissionmixin___handle_slice_access_expr
module6_whyml__expressions expressionemissionmixin___strip_outer_parens
module6_whyml__functions functionemissionmixin___compute_return_type
module6_whyml__functions functionemissionmixin___parse_mixin_sig
module6_whyml__functions functionemissionmixin___refine_tuple_return_type
module6_whyml__types typeinferencemixin___first_assign_kind
module6_whyml__types typeinferencemixin___split_tuple_type
frontend__Module1_Ingestor _match_block_hdr
proof2why3__sertop _process_sertop_line
proof2why3__sertop _sexp_tokens
L
