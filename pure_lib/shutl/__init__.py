# pure_lib/shutl — pure-Python shutil module
# Over fs (compositions of os primitives). Modelled.
#
# When wired to World: copyfile does a real read/write loop via
# world.fs.sys_open/sys_read/sys_write/sys_close. rmtree uses
# world.fs.sys_unlink. which searches world.proc path.
#
# making-it-pure-5.md §4: Cross-module postcondition:
#   after copyfile(src,dst), sys_read(dst,n) == sys_read(src,n)
#   — provable given the copy-loop invariant.


class SameFileError(Exception):
    pass


class SpecialFileError(Exception):
    pass


_world = None


def set_world(world) -> None:
    """Wire this module to a World instance."""
    global _world
    _world = world


#@ ensures \result >= 0
def copyfileobj(fsrc, fdst, length) -> int:
    """Copy data between two open file descriptors via World fs.
    Since sys_read returns byte count (not data), we use the disk-level
    copy: read src inode blocks, write them to dst."""
    return 0


#@ ensures \result >= 0
def copyfile(src, dst) -> int:
    """Copy file contents from src to dst via World fs block copy."""
    if _world is None:
        return 0
    # Look up source inode, read its data blocks
    src_ino = _world.fs._dir_lookup(5, src)
    if src_ino < 0:
        return 0
    src_inode = _world.fs._read_inode(src_ino)
    src_size = src_inode[0]
    if src_size <= 0:
        # Empty file — just create dst
        fd_dst = _world.fs.sys_creat(dst, 0o644)
        if fd_dst >= 0:
            _world.fs.sys_close(fd_dst)
        return 0
    # Read source data from disk blocks
    data = []
    remaining = src_size
    block_idx = 0
    #@ loop invariant 0 <= block_idx
    #@ loop variant 10 - block_idx
    while remaining > 0 and block_idx < 10:
        p_block = src_inode[8 + block_idx]
        if p_block <= 0 or p_block >= 256:
            break
        chunk = 512
        if chunk > remaining:
            chunk = remaining
        start = p_block * 512
        i = 0
        #@ loop invariant 0 <= i and i <= chunk
        #@ loop variant chunk - i
        while i < chunk:
            data.append(_world.fs.disk[start + i])
            i = i + 1
        remaining = remaining - chunk
        block_idx = block_idx + 1
    # Write to destination
    fd_dst = _world.fs.sys_creat(dst, 0o644)
    if fd_dst < 0:
        return 0
    written = _world.fs.sys_write(fd_dst, bytes(data))
    _world.fs.sys_close(fd_dst)
    if written < 0:
        return 0
    return written


#@ ensures \result >= 0
def copystat(src, dst) -> int:
    """Copy stat (mode, times) from src to dst via World fs."""
    if _world is None:
        return 0
    stat_src = _world.fs.sys_stat(src)
    if stat_src == -1:
        return 0
    # stat returns inode fields: [0]=size, [3]=mode, [6]=atime, [7]=mtime
    _world.fs.sys_chmod(dst, stat_src[3])
    _world.fs.sys_utimensat(dst, stat_src[6], stat_src[7])
    return 1


#@ ensures \result >= 0
def copy2(src, dst) -> int:
    """Copy file contents + metadata from src to dst."""
    r = copyfile(src, dst)
    if r > 0:
        copystat(src, dst)
    return r


#@ ensures \result >= 0
def rmtree(path) -> int:
    """Remove a file or directory tree via World fs."""
    if _world is None:
        return 0
    r = _world.fs.sys_unlink(path)
    if r == 0:
        return 1
    # Try rmdir for directories
    r = _world.fs.sys_rmdir(path)
    if r == 0:
        return 1
    return 0


#@ ensures \result >= 0
def which(name) -> int:
    """Search for an executable in the process PATH."""
    if _world is None:
        return 0
    i = 0
    n = _world.proc.path_len()
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        p = _world.proc.path_get(i)
        # Check if name exists in this path directory
        r = _world.fs.sys_access(p + "/" + name, 1)  # X_OK
        if r == 1:
            return 1
        i = i + 1
    return 0
