#!/bin/bash
# mut.sh <rel> <Qual.fn> <old> <new> <funname> <tag> : mutate stm copy, --fun, restore (NORMAL)
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI; T=$L/stm; cd $T; export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
f=src/self-annotate/src/$1; cp $f $L/mut.bak
python3 - "$f" "$2" "$3" "$4" <<'PY'
import sys; p,q,o,n=sys.argv[1:]; s=open(p).read(); fn=q.split('.')[-1]
a=s.index('    def '+fn+'('); b=s.index('\n    def ',a+10) if '\n    def ' in s[a+10:] else len(s)
seg=s[a:b]; assert seg.count(o)>=1,(o,); seg=seg.replace(o,n,1); open(p,'w').write(s[:a]+seg+s[b:]); print('mutated')
PY
mkdir -p $L/fun; timeout 9000 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --fun "$5" > $L/fun/$6.log 2>&1; echo "rc=$?" >> $L/fun/$6.log
cp $L/mut.bak $f; rm -f ${f%.py}.mlw
