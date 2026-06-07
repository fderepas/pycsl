# pure_lib/proc — pure-Python process state model
# Named 'proc' to avoid stdlib name clash.
#
# Models Unix process state: pid, creds, cwd, environ, argv, umask.
# Unix skill §6 (process model), §7.2 (environment).
#
# Owns world.proc.* — no method outside this module writes these fields.
# (Confinement via proc_ownership HAPPY, §2.1 of making-it-pure-5.md)


#@ class invariant self.pid >= 0
#@ class invariant self.ppid >= 0
#@ class invariant self.uid >= 0
#@ class invariant self.gid >= 0
#@ class invariant self.umask >= 0
#@ class invariant self.cwd_inode >= 0
#@ class invariant self.exit_code >= -1
#@ class invariant self._argc >= 0
#@ class invariant self._env_count >= 0
#@ class invariant self._path_count >= 0
class ProcessState:
    """Unix process state — owns pid, creds, cwd, environ, argv.

    Takes references to the shared filesystem and clock so that
    chdir() can validate the cwd inode exists, and time-stamped
    operations (e.g. accounting) can use the same clock.
    """

    def __init__(self, fs=None, clock=None):
        self.pid = 1
        self.ppid = 0
        self.uid = 0
        self.gid = 0
        self.umask = 18  # 0o022 = 18 decimal
        self.cwd_inode = 0  # root inode
        self.exit_code = -1  # -1 means "still running"
        self._fs = fs
        self._clock = clock
        # argv, environ, path as parallel lists (PyCSL-friendly)
        # Explicit size fields because PyCSL can't do len() on arrays.
        self._argv_keys: list = []
        self._argc = 0
        self._env_keys: list = []
        self._env_vals: list = []
        self._env_count = 0
        self._path: list = []
        self._path_count = 0

    # --- argv ---

    #@ assigns \nothing
    #@ ensures \result >= 0
    def argc(self) -> int:
        return self._argc

    #@ requires index >= 0
    #@ assigns \nothing
    def argv(self, index: int) -> str:
        if index < self._argc:
            return self._argv_keys[index]
        return ""

    #@ assigns self._argv_keys, self._argc
    def set_argv(self, args: list) -> None:
        self._argv_keys = args
        self._argc = len(args)

    # --- environ ---

    #@ assigns \nothing
    def getenv(self, key: str, default: str = "") -> str:
        i = 0
        n = self._env_count
        #@ loop invariant 0 <= i and i <= n
        #@ loop variant n - i
        while i < n:
            if self._env_keys[i] == key:
                return self._env_vals[i]
            i = i + 1
        return default

    #@ assigns self._env_keys, self._env_vals, self._env_count
    def setenv(self, key: str, value: str) -> None:
        i = 0
        n = self._env_count
        #@ loop invariant 0 <= i and i <= n
        #@ loop variant n - i
        while i < n:
            if self._env_keys[i] == key:
                self._env_vals[i] = value
                return
            i = i + 1
        self._env_keys.append(key)
        self._env_vals.append(value)
        self._env_count = self._env_count + 1

    #@ assigns self._env_keys, self._env_vals, self._env_count
    def unsetenv(self, key: str) -> None:
        i = 0
        n = self._env_count
        #@ loop invariant 0 <= i and i <= n
        #@ loop variant n - i
        while i < n:
            if self._env_keys[i] == key:
                self._env_keys.pop(i)
                self._env_vals.pop(i)
                self._env_count = self._env_count - 1
                return
            i = i + 1

    # --- cwd ---

    #@ assigns self.cwd_inode
    #@ ensures self.cwd_inode >= 0
    #@ ensures \result == 0 or \result == -1
    def chdir(self, inode_num: int) -> int:
        """Change cwd to the given inode. Returns 0 on success, -1 on error.
        If fs is wired, validates the inode exists and is a directory."""
        if inode_num < 0 or inode_num >= 32:
            return -1
        if self._fs is not None:
            inode = self._fs._read_inode(inode_num)
            if inode[2] != 2:  # not a directory
                return -1
        self.cwd_inode = inode_num
        return 0

    #@ assigns \nothing
    #@ ensures \result >= 0
    def getcwd_inode(self) -> int:
        return self.cwd_inode

    # --- umask ---

    #@ assigns self.umask
    #@ ensures \result >= 0
    def umask_set(self, new_umask: int) -> int:
        old = self.umask
        if new_umask >= 0:
            self.umask = new_umask
        return old

    # --- exit ---

    #@ assigns self.exit_code
    #@ ensures self.exit_code == code
    def exit(self, code: int) -> None:
        self.exit_code = code

    # --- path ---

    #@ assigns self._path, self._path_count
    def set_path(self, path_list: list) -> None:
        self._path = path_list
        self._path_count = len(path_list)

    #@ assigns \nothing
    #@ ensures \result >= 0
    def path_len(self) -> int:
        return self._path_count

    #@ requires index >= 0
    #@ assigns \nothing
    def path_get(self, index: int) -> str:
        if index < self._path_count:
            return self._path[index]
        return ""
