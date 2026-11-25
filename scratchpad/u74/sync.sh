#!/bin/bash
# sync the worktree src/pycsl into the scratch probe tree
rsync -a --delete --exclude '__pycache__' --exclude '*.mlw' /home/fabrice/git/pycsl-u74/src/pycsl/ /home/fabrice/git/pycsl-u74/scratchpad/u74/st/src/pycsl/
