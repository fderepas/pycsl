"""PyCSL mock for Python's subprocess module.

Provides trusted stubs for subprocess management: process creation,
Popen lifecycle, CompletedProcess results, and associated constants.
CompletedProcess and PopenObj modelled as classes with invariants.
"""
_ = 0  # anchor

# ── Constants ───────────────────────────────────────────────────────

DEVNULL = -3
PIPE = -1
STDOUT = -2

# ── CompletedProcess class ──────────────────────────────────────────

""  # pycsl
#@ class invariant self._returncode >= -128
class CompletedProcessObj:
    def __init__(self):
        self._returncode = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def args(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._returncode
    #@ assigns \nothing
    def returncode(self) -> int:
        return self._returncode

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def stdout(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def stderr(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns \nothing
    def check_returncode(self) -> int:
        return 0

# ── PopenObj class ──────────────────────────────────────────────────

#@ class invariant self._pid >= 0
class PopenObj:
    def __init__(self):
        self._pid = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= -1
    #@ assigns \nothing
    def poll(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= -128
    #@ assigns \nothing
    def wait(self, timeout: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def communicate(self, inp: int, timeout: int) -> int:
        return 0

    #@ \trusted
    #@ requires signal >= 0
    #@ ensures \result == 0
    #@ assigns \nothing
    def send_signal(self, signal: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns \nothing
    def terminate(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns \nothing
    def kill(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def args(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._pid
    #@ assigns \nothing
    def pid(self) -> int:
        return self._pid

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= -128
    #@ assigns \nothing
    def returncode(self) -> int:
        return 0

# ── High-level convenience functions ────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def run(args: int, stdin: int, inp: int, stdout: int, stderr: int, capture_output: int, shell: int, cwd: int, timeout: int, chk: int, encoding: int, errors: int, text: int, env: int, universal_newlines: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def call(args: int, stdin: int, stdout: int, stderr: int, shell: int, cwd: int, timeout: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_call(args: int, stdin: int, stdout: int, stderr: int, shell: int, cwd: int, timeout: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_output(args: int, stdin: int, stderr: int, shell: int, cwd: int, encoding: int, errors: int, universal_newlines: int, timeout: int, text: int) -> int:
    return 0

# ── Exceptions ─────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def SubprocessError() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def TimeoutExpired(cmd: int, timeout: int, output: int, stdout: int, stderr: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def CalledProcessError(rcode: int, cmd: int, output: int, stdout: int, stderr: int) -> int:
    return 0

# ── Legacy shell invocation ────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def getstatusoutput(cmd: int, encoding: int, errors: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def getoutput(cmd: int, encoding: int, errors: int) -> int:
    return 0
