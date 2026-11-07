#!/bin/bash
# Full three-plane battery, driver-verified fresh. Run from the repo root.
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/tmp
mkdir -p "$TMPDIR"
cd /home/fabrice/git/pycsl
echo "=== markers (x3) ==="
for i in 1 2 3; do python3 bin/count-trusted-directives.py | head -1; sleep 1; done
echo "=== corpus byte-diff vs window-start base ==="
bash bin/byte-diff-sweep.sh /home/fabrice/git/pycsl/scratchpad/w4/corp_fin2 2>&1 | tail -1
echo "differing: $(diff -rq scratchpad/w4/corp_base scratchpad/w4/corp_fin2 | wc -l)"
echo "=== mirror emission diff vs window-start base ==="
find src/self-annotate -name '*.mlw' ! -name 'pycsl-wp-spec.mlw' -delete
bash scratchpad/mirror_md5.sh /home/fabrice/git/pycsl > scratchpad/w4/md5_end.txt 2>&1
diff <(sed 's#scratchpad/w4/base/##' scratchpad/w4/md5_base.txt) scratchpad/w4/md5_end.txt | grep '^>' | awk '{print "  moved: "$3}'
echo "=== L3-tc sweep ==="
ok=0; fail=""
for f in $(find src/self-annotate/src -name '*.py' | sort); do
  r=$(PYTHONHASHSEED=0 timeout 300 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --no-proof 2>&1 | grep -c "L3-tc ✓")
  if [ "$r" -ge 1 ]; then ok=$((ok+1)); else fail="$fail $f"; fi
done
echo "L3-tc GREEN: $ok / 52; FAIL:$fail"
echo "=== fidelity ==="
echo "sync DIVERGED: $(bash bin/check-self-annotate-sync.sh 2>&1 | grep -c '^DIVERGED')"
echo "mirror-sync DIVERGED: $(python3 bin/check-self-annotate-mirror-sync.py 2>&1 | grep -c '^DIVERGED')"
echo "=== vacuity ==="; python3 bin/check-emitted-vacuity.py --emit 2>&1 | tail -1
echo "=== shadowed ==="; python3 bin/check-shadowed-selfcalls.py 2>&1 | tail -1
echo "=== frame-honesty ==="; python3 bin/check-trusted-frame-honesty.py 2>&1 | tail -1
echo "=== untrusted-emitted ==="; python3 bin/check-untrusted-emitted.py 2>&1 | tail -1
echo "=== yield-erasure ==="; python3 bin/check-yield-erasure.py 2>&1 | tail -1
echo "=== mirror-signature-drift ==="; python3 bin/check-mirror-signature-drift.py 2>&1 | head -1; python3 bin/check-mirror-signature-drift.py >/dev/null 2>&1; echo "  drift exit=$?"
find src/self-annotate -name '*.mlw' ! -name 'pycsl-wp-spec.mlw' -delete
echo "=== BATTERY DONE ==="
