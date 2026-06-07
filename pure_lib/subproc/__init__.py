# pure_lib/subproc — pure-Python subprocess module
# ProcessModel: Modelled plumbing (pipes, returncode). Child execution: Stubbed.
# Unix skill §7.1 (fork), §5.7 (pipes), §7.4 (wait).
#
# When wired to World: Popen creates pipe FDs via world.fs for
# stdin/stdout/stderr plumbing. Child execution remains stubbed
# (the child process is a black box — TCB entry).


class CalledProcessError(Exception):
    def __init__(self, returncode, cmd, output, stderr):
        self.returncode = returncode
        self.cmd = cmd
        self.output = output
        self.stderr = stderr


class TimeoutExpired(Exception):
    def __init__(self, cmd, timeout, output, stderr):
        self.cmd = cmd
        self.timeout = timeout
        self.output = output
        self.stderr = stderr


class SubprocessError(Exception):
    pass


class CompletedProcess:
    def __init__(self, args, returncode, stdout, stderr):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


_world = None


def set_world(world) -> None:
    """Wire this module to a World instance."""
    global _world
    _world = world


#@ class invariant self._returncode >= -1
class Popen:
    def __init__(self, args):
        self._args = args
        self._returncode = -1
        self._stdin_pipe = []
        self._stdout_pipe = []
        self._stderr_pipe = []
        self._pid = 0
        if _world is not None:
            self._pid = _world.proc.pid

    #@ ensures \result >= -1
    def poll(self) -> int:
        return self._returncode

    #@ ensures \result >= -1
    def wait(self) -> int:
        return self._returncode

    #@ ensures \result[0] >= 0
    #@ ensures \result[1] >= 0
    def communicate(self, input_data) -> tuple:
        if input_data != 0:
            self._stdin_pipe = input_data
        self._returncode = 0
        return (self._stdout_pipe, self._stderr_pipe)

    #@ ensures \result == self._returncode
    def returncode(self) -> int:
        return self._returncode


#@ ensures \result >= 0
def list2cmdline(seq) -> int:
    return 0


#@ ensures \result.returncode >= 0
def run(args, capture_output, check) -> CompletedProcess:
    p = Popen(args)
    out = p.communicate(0)
    stdout = out[0]
    stderr = out[1]
    rc = p.wait()
    result = CompletedProcess(args, rc, stdout, stderr)
    if check != 0:
        if rc != 0:
            raise CalledProcessError(rc, args, stdout, stderr)
    return result
