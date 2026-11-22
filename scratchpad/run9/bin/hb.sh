#!/bin/bash
sleep ${1:-1800}; NOW=$(date +%s); DL=$(cat /home/fabrice/git/pycsl/getting-better/.driver-deadline 2>/dev/null || echo 0)
if [ "$NOW" -lt "$DL" ]; then echo "HEARTBEAT — $(( (DL-NOW)/60 )) min left; resume the driver loop at A.2"; else echo "HEARTBEAT — deadline passed; finish per A.3"; fi
