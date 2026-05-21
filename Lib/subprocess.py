"""PyCSL mock for Python's subprocess module — Subprocess management."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def run(args: int, stdin: int, input: int, stdout: int, stderr: int, __capture_output: int, shell: int) -> int:
    """Mock: Run the command described by *args*.  Wait for command to complete, then return a :class:`CompletedProcess` instance. Th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def call(args: int, stdin: int, stdout: int, stderr: int, __shell: int, cwd: int, timeout: int) -> int:
    """Mock: Run the command described by *args*.  Wait for command to complete, then return the :attr:`~Popen.returncode` attribute...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_call(args: int, stdin: int, stdout: int, stderr: int, __shell: int, cwd: int, timeout: int) -> int:
    """Mock: Run command with arguments.  Wait for command to complete. If the return code was zero then return, otherwise raise :exc..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def check_output(args: int, stdin: int, stderr: int, shell: int, __cwd: int, encoding: int, errors: int) -> int:
    """Mock: Run command with arguments and return its output. If the return code was non-zero it raises a :exc:`CalledProcessError`...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getstatusoutput(cmd: int, encoding: int, errors: int) -> int:
    """Mock: Return ``(exitcode, output)`` of executing *cmd* in a shell. Execute the string *cmd* in a shell with :func:`check_outpu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getoutput(cmd: int, encoding: int, errors: int) -> int:
    """Mock: Return output (stdout and stderr) of executing *cmd* in a shell. Like :func:`getstatusoutput`, except the exit code is i..."""
    return 0
