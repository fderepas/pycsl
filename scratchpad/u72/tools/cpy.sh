#!/bin/bash
# cpy.sh <dir> <files...> : CPython run of each probe (cwd = <dir>, ulimit'd, -B -E -s)
D=$1; shift; cd $D || exit 2
for f in "$@"; do
  o=$(timeout 60 bash -c "ulimit -v 2000000; python3 -B -E -s $(basename $f) 2>&1" | tail -1 | cut -c1-120)
  echo "$(basename $f .py) :: $o"
done
