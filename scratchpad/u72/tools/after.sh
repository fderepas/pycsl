#!/bin/bash
# after.sh <pid> <cmd...> : wait for <pid> to exit, then run <cmd...>
P=$1; shift; while kill -0 $P 2>/dev/null; do sleep 20; done; exec "$@"
