# mkwit.py <worktree> : copy the selected red-team witnesses into the corpus (IDs from 6250)
import sys, os, re
T = sys.argv[1]
W = T + '/getting-better/open-routes/'
C = T + '/test-suite/corpus/pycsl-reference/'
sel = [('421', 'b00 b01 b02 b04 b07 b09 b11 b12 b13 b17 b18 b20 b21 b22 b23 b33 b41 b44 b52 b54 b55 b56 b60 b68 b69 b70 b71 b72 h03 h07 h16 h19'),
       ('422', 'c27 c31 c35'),
       ('423', 'a20 a23 a25 a27 a34 j00 j01 j02 j04 j05 j08 j09'),
       ('424', 'a10 j23'),
       ('425', 'd14 d22 n01 n07'),
       ('426', 'e09 e12 f00 f01 f12 m01 m05'),
       ('427', 'g07 m10 m13 m14 w11 w12'),
       ('428', 'i01 i05 i07 i15 i21 t01 t04')]
n = 6250
for r, ks in sel:
    d = W + 'witnesses-r' + r + '/'
    fs = sorted(os.listdir(d))
    for k in ks.split():
        f = [x for x in fs if x.startswith(k + '_')]
        assert len(f) == 1, (r, k, f)
        src = open(d + f[0]).read()
        stem = f[0][:-3]
        out = C + '%04d_r%s_%s.py' % (n, r, stem)
        hdr = ('r"""Test %04d -- route #%s (expected FAIL): red team 33 witness `%s` (getting-better/open-routes/witnesses-r%s/%s). '
               'PROVED at base ac28806be; CPython violates the claim (the `__main__` driver prints VIOLATION).\n"""\n# pycsl-expected: FAIL\n'
               % (n, r, stem, r, f[0]))
        open(out, 'w').write(hdr + src)
        print(os.path.basename(out))
        n += 1
