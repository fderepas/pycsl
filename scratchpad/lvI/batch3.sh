#!/bin/bash
# --fun gates on the st tree (= candidate), mutations on stm, witnesses (NORMAL, sequential)
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI; S=$L/st
$L/fun.sh $S module6_whyml/expressions.py expressionemissionmixin___emit_bitwise_or_power bw1
$L/fun.sh $S module6_whyml/statements.py statementemissionmixin___handle_augassign_stmt aug1
$L/fun.sh $S module6_whyml/statements.py statementemissionmixin___handle_fieldassign_stmt fa1
$L/mut.sh module6_whyml/expressions.py ExpressionEmissionMixin._e '        _sub: Dict[str, str] = {}' '        self._scope_dyn_exec = True
        _sub: Dict[str, str] = {}' expressionemissionmixin___e m_e
$L/mut.sh module6_whyml/expressions.py ExpressionEmissionMixin._emit_bitwise_or_power '        left_ir = expr.get("left", {})' '        self._in_spec = True
        left_ir = expr.get("left", {})' expressionemissionmixin___emit_bitwise_or_power m_bw
$L/mut.sh module6_whyml/statements.py StatementEmissionMixin._handle_augassign_stmt '        safe_target = whyml_ident(target)' '        self._heap_var = "x"
        safe_target = whyml_ident(target)' statementemissionmixin___handle_augassign_stmt m_aug
$L/batch1.sh
echo done > $L/b3.done
