#!/usr/bin/env bash
# Canonical CPU-count helper — SOURCE this; never roll your own nproc/2.
# Single source of truth for bin/run-reference-tests.sh and bin/byte-diff-sweep.sh.

# get_cpu_count — total logical CPUs on Ubuntu/Linux or macOS (more-proc.md §4.5, verbatim).
get_cpu_count() {
    case "$(uname -s)" in
        Linux)
            # nproc respects cgroup/affinity limits; fall back if absent
            if command -v nproc >/dev/null 2>&1; then
                nproc
            else
                getconf _NPROCESSORS_ONLN 2>/dev/null || \
                grep -c '^processor' /proc/cpuinfo
            fi
            ;;
        Darwin)
            # logical CPUs (includes Hyper-Threading); use hw.physicalcpu for physical cores
            sysctl -n hw.logicalcpu 2>/dev/null || \
            sysctl -n hw.ncpu
            ;;
        *)
            # last-ditch POSIX fallback
            getconf _NPROCESSORS_ONLN 2>/dev/null || echo 1
            ;;
    esac
}

# half_cpu_jobs — the courtesy budget: EXACTLY half the logical cores (min 1).
half_cpu_jobs() { local c h; c=$(get_cpu_count); h=$(( c / 2 )); [ "$h" -lt 1 ] && h=1; echo "$h"; }
