#!/bin/bash
cd /home/fabrice.derepas@canonical.com/git/pycsl
for f in __init__ _poke _write_inode _zero_entry _write_entry sys_chmod sys_unlink sys_rmdir sys_rename; do
  out=".audit-cache/m4-baseline/$f.txt"
  PYTHONPATH=src/pycsl .venv/bin/python -m pycsl pure_lib/os/UnixInodeFileSystem.py --fun "unixinodefilesystem__$f" > "$out" 2>&1
  nonvalid=$(grep -ciE "Timeout|Unknown|Out of memory|Failure|Invalid|Step limit|Resource" "$out")
  valid=$(grep -ciE "\bValid\b" "$out")
  echo "$f: Valid=$valid nonValid=$nonvalid" >> .audit-cache/m4-baseline/SUMMARY.txt
done
echo "DONE" >> .audit-cache/m4-baseline/SUMMARY.txt
