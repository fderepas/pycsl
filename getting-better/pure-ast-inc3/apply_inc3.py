import sys
p2='src/pycsl/frontend/ir_resolve.py'
t=open(p2).read()
old2='''    "Expression": [("body", "ExprIR")],'''
new2='''    "Expression": [("body", "ExprIR")],
    # CLASS-BY-NAME FACTORY vein: `comprehension` is the `for`-clause of a comp/genexp —
    # `_NODE_SPEC['comprehension'] == ('AST', ('target','iter','ifs','is_async'), ())`, four
    # TOTAL fields (no `_OPTIONAL_FIELDS` entry). `target`/`iter` are expr children;
    # `ifs` is a LIST of expr children (the "ExprIRList" tag -> `array emit_ir`);
    # `is_async` is the 0/1 flag the live `comp_for` body sets literally.
    "comprehension": [("target", "ExprIR"), ("iter", "ExprIR"),
                      ("ifs", "ExprIRList"), ("is_async", "int")],'''
assert t.count(old2)==1
t=t.replace(old2,new2); open(p2,'w').write(t)

p3='src/self-annotate/src/frontend/pure_ast.py'
u=open(p3).read()
for name in ("or_test", "or_test_no_cond", "_comp_target"):
    old3='''    #@ \\trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def %s(self):
        pass''' % name
    new3='''    # RETURN INTERFACE + CURSOR NON-REGRESSION (the `error -> "NoReturn"` / `_name_str`
    # precedents). STAYS \\trusted. `-> "ExprIR"` records that the result IS an expression
    # node (`emit_ir`), so it can be bound into a harvested record's expr child instead of
    # an opaque int. `ensures self.i >= \\old(self.i)` is a TRUSTED-INTERFACE claim backed by
    # the live body: every `_Parser` descent moves the cursor only through `advance` /
    # `accept_*` / `expect_*`, none of which decreases `self.i`. A caller's cursor-measure
    # loop needs it from EVERY call in its body, not just from the guard (relaunch #4's
    # measured lesson on `_name_str`).
    #@ \\trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ ensures self.i >= \\old(self.i)
    #@ assigns self.i
    def %s(self) -> "ExprIR":
        pass''' % name
    assert u.count(old3)==1, name
    u=u.replace(old3,new3)
old4='''    #@ \\trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def comp_for(self):
        pass'''
new4='''    # CLASS-BY-NAME FACTORY vein, increment 3: CONVERTED. Verbatim body port of the LIVE
    # `comp_for`. Both cursor-measure loops discharge (the outer through `expect_kw`'s new
    # UNCONDITIONAL strict progress, the inner through `at_kw` + `advance`), the `ifs`
    # accumulator really carries the parsed conditions into the record's list field, and the
    # returned `List[comprehension]` is the harvested record list.
    #@ requires True
    #@ ensures True
    #@ assigns self.i
    def comp_for(self) -> "List[comprehension]":
        gens = []
        #@ loop invariant 0 <= self.i and self.i < \\length(self.toks)
        #@ loop variant \\length(self.toks) - self.i
        while self.at_kw("for") or (self.at_kw("async") and self.peek(1).string == "for"):
            is_async = 0
            if self.at_kw("async"):
                self.advance(); is_async = 1
            self.expect_kw("for")
            target = self._comp_target()
            self.expect_kw("in")
            it = self.or_test()
            ifs = []
            #@ loop invariant 0 <= self.i and self.i < \\length(self.toks)
            #@ loop variant \\length(self.toks) - self.i
            while self.at_kw("if"):
                self.advance()
                ifs.append(self.or_test_no_cond())
            gens.append(_N("comprehension")(target=target, iter=it, ifs=ifs, is_async=is_async))
        return gens'''
assert u.count(old4)==1
u=u.replace(old4,new4); open(p3,'w').write(u)
print('inc3 pure_ast+ir_resolve applied')
