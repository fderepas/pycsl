import io,sys
p='src/self-annotate/src/frontend/pure_ast.py'
s=open(p).read()
old = '''    #@ \\trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ ensures self.i >= \\old(self.i)
    #@ assigns self.i
    def _binop(self, min_prec) -> "ExprIR":
        pass
'''
assert s.count(old)==1, s.count(old)
new = '''    #@ requires True
    #@ ensures True
    #@ ensures self.i >= \\old(self.i)
    #@ \\variant 13 * (\\length(self.toks) - self.i) + 12
    #@ assigns self.i
    def _binop(self, min_prec) -> "ExprIR":
        t = self.cur()
        left = self.factor()
        #@ ghost i90 = self.i
        #@ loop invariant 0 <= self.i and self.i < \\length(self.toks)
        #@ loop invariant self.i >= i90
        #@ loop variant \\length(self.toks) - self.i
        while self.cur().type == _tokenize.OP and self.cur().string in _BINOP:
            opname, prec = _BINOP[self.cur().string]
            if prec < min_prec:
                break
            self.advance()
            right = self._binop(prec + 1)
            left = _N("BinOp")(left=left, op=_N(opname)(), right=right)
            left.lineno = t.start[0]; left.col_offset = t.start[1]
            left.end_lineno = right.end_lineno; left.end_col_offset = right.end_col_offset
        return left
'''
open(p,'w').write(s.replace(old,new))
print("patched")
