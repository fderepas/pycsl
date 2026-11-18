#!/bin/bash
# Build the r12 probe dirs under ./cases (idempotent: wipes ./cases first).
set -e
P=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY=/home/fabrice/git/pycsl/.venv/bin/python
cd "$P"; rm -rf ./cases; mkdir cases
STD=/usr/lib/python3.14
mk() { mkdir -p cases/$1; cp $P/$2 cases/$1/; }
hcase() { mk $1 prog_hash.py; cp $STD/hashlib.py cases/$1/; }
jcase() { mk $1 prog_json.py; mkdir cases/$1/json; cp $STD/json/*.py cases/$1/json/; }
ncase() { mk $1 prog_mylib.py; cp $P/mylib.py cases/$1/; }
hcase A0_hash_nocache
hcase A1_hash_forged_unchecked;  $PY -I forge.py unchecked evil_hashlib.py cases/A1_hash_forged_unchecked/hashlib.py
hcase A2_hash_forged_timestamp;  $PY -I forge.py timestamp evil_hashlib.py cases/A2_hash_forged_timestamp/hashlib.py
hcase A3_hash_forged_checked_badhash; $PY -I forge.py checked evil_hashlib.py cases/A3_hash_forged_checked_badhash/hashlib.py
hcase A4_hash_forged_stale_ts;   $PY -I forge.py stale evil_hashlib.py cases/A4_hash_forged_stale_ts/hashlib.py
hcase A5_hash_genuine_ts;        $PY -I forge.py genuine x cases/A5_hash_genuine_ts/hashlib.py
hcase A5u_hash_genuine_unchecked; $PY -I forge.py genuine-unchecked x cases/A5u_hash_genuine_unchecked/hashlib.py
hcase A5o_hash_genuine_opt12;    $PY -I forge.py genuine x cases/A5o_hash_genuine_opt12/hashlib.py 1; $PY -I forge.py genuine x cases/A5o_hash_genuine_opt12/hashlib.py 2; $PY -I forge.py genuine x cases/A5o_hash_genuine_opt12/hashlib.py
hcase A6_hash_forged_opt1;       $PY -I forge.py genuine x cases/A6_hash_forged_opt1/hashlib.py; $PY -I forge.py unchecked evil_hashlib.py cases/A6_hash_forged_opt1/hashlib.py 1
hcase A7_hash_forged_opt2;       $PY -I forge.py unchecked evil_hashlib.py cases/A7_hash_forged_opt2/hashlib.py 2
hcase A8_hash_otherver;          mkdir -p cases/A8_hash_otherver/__pycache__; $PY -I forge.py unchecked evil_hashlib.py cases/A8_hash_otherver/hashlib.py; mv cases/A8_hash_otherver/__pycache__/hashlib.cpython-314.pyc cases/A8_hash_otherver/__pycache__/hashlib.cpython-313.pyc
jcase J0_json_nocache
jcase J1_json_forged_init_unchecked; $PY -I forge.py unchecked evil_json_init.py cases/J1_json_forged_init_unchecked/json/__init__.py
jcase J2_json_genuine_copied;    mkdir cases/J2_json_genuine_copied/json/__pycache__; cp -p /home/fabrice/git/pycsl/json/__pycache__/*.pyc cases/J2_json_genuine_copied/json/__pycache__/; touch -r /home/fabrice/git/pycsl/json/__init__.py cases/J2_json_genuine_copied/json/*.py
ncase N0_mylib_nocache
ncase N1_mylib_forged_unchecked; $PY -I forge.py unchecked evil_mylib.py cases/N1_mylib_forged_unchecked/mylib.py
ncase N2_mylib_genuine;          $PY -I forge.py genuine x cases/N2_mylib_genuine/mylib.py
ls cases
hcase A9_hash_forged_opt3;       $PY -I forge.py unchecked evil_hashlib.py cases/A9_hash_forged_opt3/hashlib.py 2; mv cases/A9_hash_forged_opt3/__pycache__/hashlib.cpython-314.opt-2.pyc cases/A9_hash_forged_opt3/__pycache__/hashlib.cpython-314.opt-3.pyc
hcase A5r_hash_real_cpython_cache; (cd cases/A5r_hash_real_cpython_cache && for o in "" -O -OO -OOO; do $PY -E -s $o -c "import hashlib" ; done; ls __pycache__)
tcase() { mk $1 prog_toml.py; mkdir cases/$1/tomllib; cp $STD/tomllib/*.py cases/$1/tomllib/; }
tcase T0_toml_nocache
tcase T1_toml_forged_submodule_unchecked; $PY -I forge.py unchecked evil_toml_parser.py cases/T1_toml_forged_submodule_unchecked/tomllib/_parser.py
tcase T2_toml_genuine_unchecked; for m in cases/T2_toml_genuine_unchecked/tomllib/*.py; do $PY -I forge.py genuine-unchecked x $m; done
