#!/usr/bin/env bash
# screen-conversion-candidate.sh — RUN THE CONVERSION CRITERION ON ONE CANDIDATE, BEFORE
# SPENDING PROVER TIME ON IT.
#
# WHY THIS EXISTS (#49, gen #31). Retiring a `\trusted` marker was screened by two things:
# does the ported body TYPE-CHECK (`--no-proof`), and does the whole file PROVE. Neither
# answers the question the campaign is actually asking, which is whether the conversion is
# WORTH ANYTHING. Six conversions landed in one session passed both and were hollow: five
# emitted bodies ignored every input their live body uses, and one dropped a generator's
# yielded values. See
# getting-better/open-routes/finding-check-one-is-a-quarter-of-the-criterion.md.
#
# The four oracles that answer it take ~5 minutes on a COPY of the tree. The cheapest
# candidate in the mirror costs 11 seconds to prove and the most expensive costs THREE
# HOURS, so screening first is not a tax, it is the whole economy: the first candidate this
# script was written for (`pure_ast.py::NodeVisitor.generic_visit`) was refused in five
# minutes instead of after two and a half hours of `pure_ast.py`.
#
# USAGE
#     bin/screen-conversion-candidate.sh <mirror/relative/path.py> <Qualified.Name> [--replace]
#
#   <path.py>        relative to src/self-annotate/src
#   <Qualified.Name> the FULL nested qualname, exactly as getting-better/trusted-reasons.tsv
#                    spells it (`Class.method`, `Class.method.inner`)
#   --replace        the mirror body is a REAL body, not a `pass` facade, and replacing it
#                    with the live twin is the point (the DIFFERS population)
#
# WHAT IT DOES. Copies `src` + `bin` at HEAD into a scratch tree, ports the live body over
# the mirror one, deletes the governing `#@ \trusted` line, emits, and runs:
#
#     check-untrusted-emitted.py    emitted as a DEFINITION, not re-abstracted to a `val`
#     check-yield-erasure.py        a generator's yielded VALUES survive
#     check-shadowed-selfcalls.py   the CALLERS can see the body
#     check-emitted-vacuity.py      the emitted body USES the inputs the live body uses
#
# It does NOT prove anything and it does NOT touch the working tree. A green result is a
# LICENCE TO SPEND PROVER TIME, never a licence to land: check 1 (the emit-diff, four
# clauses) and check 0 (no un-trusted closure inside a `\trusted` parent) are still read by
# a human, and the three L-planes still gate the increment.
#
# EXIT  0 all four green · 1 at least one refused · 2 the port itself could not be done
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REL="${1:-}"; FN="${2:-}"; EXTRA="${3:-}"
if [ -z "$REL" ] || [ -z "$FN" ]; then
    sed -n '2,40p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
fi
if ! command -v why3 >/dev/null 2>&1; then
    echo "[!] screen-conversion-candidate: REFUSING — \`why3\` is not on PATH; the emission"
    echo "    type-checks with it and three of the four oracles read that emission."
    echo "    THIS IS A REFUSAL, NOT A PASS."
    exit 2
fi
T="$(mktemp -d "${TMPDIR:-/tmp}/pycsl-candidate.XXXXXX")"
trap 'rm -rf "$T"' EXIT
FREE=$(df -Pk "$T" | awk 'NR==2{print $4}')
if [ "$FREE" -lt 400000 ]; then
    echo "[!] screen-conversion-candidate: REFUSING — only ${FREE}K free on the scratch"
    echo "    filesystem. A truncated copy produced a FALSE SOUNDNESS ALARM once."
    exit 2
fi
# `json` IS LOAD-BEARING AND IT IS NOT UNDER `src`. `ir_resolve._resolve_module_path`
# searches the main file's directory, **os.getcwd()**, `<tree>/src`, `src/pycsl/Lib` and
# the `--import-path` roots — and this repository has a TRACKED `json/` package AT THE
# ROOT, which is what `import json` in the mirror resolves to via CWD. A scratch tree
# built from `src` alone therefore emits `[*] Import 'json.loads': external module, no
# local source found — skipping` and produces `pycsl.mlw` and `audit_proof_reverify.mlw`
# SHORT BY the json stubs (11 lines, two `exception` declarations and four `val`s).
# MEASURED: adding `json` makes the scratch emission byte-identical to the repo's.
# Without it, an oracle screens a DIFFERENT PROGRAM from the one that will be gated.
# See getting-better/wall-lessons.md (s6).
(cd "$ROOT" && git archive HEAD src bin json) | tar -x -C "$T" || { echo "[!] git archive failed"; exit 2; }
PORTER="$SCRIPT_DIR/port-one-mirror-body.py"
if [ ! -f "$PORTER" ]; then
    echo "[!] screen-conversion-candidate: $PORTER is missing — it is the porter this script drives."
    exit 2
fi
msg=$(python3 "$PORTER" "$T" "$REL" "$FN" --convert $EXTRA 2>&1)
case "$msg" in
    ABORT*) echo "[!] $msg"; exit 2;;
esac
echo "[*] $msg"
rc=0
cd "$T" || exit 2
for plane in check-untrusted-emitted.py check-yield-erasure.py check-shadowed-selfcalls.py; do
    out=$(timeout 3000 python3 "bin/$plane" 2>&1); prc=$?
    [ "$prc" -eq 0 ] && verdict="ok  " || { verdict="RED "; rc=1; }
    printf '    %s %-32s %s\n' "$verdict" "$plane" "$(echo "$out" | tail -1 | cut -c1-110)"
done
out=$(timeout 3000 python3 bin/check-emitted-vacuity.py --emit 2>&1); prc=$?
[ "$prc" -eq 0 ] && verdict="ok  " || { verdict="RED "; rc=1; }
printf '    %s %-32s %s\n' "$verdict" "check-emitted-vacuity.py" "$(echo "$out" | tail -1 | cut -c1-110)"
if [ "$rc" -eq 0 ]; then
    echo "[+] screen-conversion-candidate: $REL::$FN — all four oracles green. This is a"
    echo "    LICENCE TO SPEND PROVER TIME, not a licence to land (check 0, check 1 and the"
    echo "    three L-planes are still owed)."
else
    echo "[!] screen-conversion-candidate: $REL::$FN — REFUSED. Do not spend prover time on it."
fi
exit $rc
