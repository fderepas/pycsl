#!/usr/bin/env bash
# Remove landed worktrees (branches wip/g29-* are kept). One at a time, each capped.
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd /home/fabrice/git/pycsl
for w in wtL wtM wtN wtO wtP wtQ wtR wtS wtT wtU wtV wtW wtX wtY; do
  if [ -d "$S/$w" ]; then
    rm -f "$S/$w/.venv"
    timeout 300 git worktree remove --force "$S/$w" < /dev/null
    echo "$w rc=$?"
  fi
done
echo CLEANUP-DONE $(date -u +%H:%M:%SZ)
