"""Runtime-only loader: populate a UnixInodeFileSystem from a real host
directory.

NOT part of the PyCSL-verified surface. It performs host filesystem I/O
(`os.walk`, reading real files) — inherently unverifiable external effects —
and drives the *verified* syscalls (`sys_open`/`sys_write`/`sys_close`) to copy
file content onto the in-memory disk. It is imported lazily by
`UnixInodeFileSystem.__init__` only when a `load_dir` is supplied, so the
verified module never depends on it.

Model limits (documented truncation): the kernel's root directory holds up to
16 entries; names are 30 bytes; each file stores one 512-byte direct block.
Files are loaded flat by basename (recursion visits every file under the tree,
but they all land in the single root directory).
"""

import os


def load_host_dir(fs, root):
    """Recursively copy files under host path `root` into `fs`.

    Returns the number of files loaded.
    """
    loaded = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            host_path = os.path.join(dirpath, name)
            try:
                with open(host_path, "rb") as f:
                    data = f.read(512)
            except OSError:
                continue
            fd = fs.sys_open(name[:30], fs.O_WRONLY | fs.O_CREAT)
            if fd < 0:
                continue
            # The verified create path leaves the inode's data block
            # unallocated; allocate one so the write lands somewhere.
            inode_num = fs.fd_inode[fd]
            inode = fs._read_inode(inode_num)
            if inode[8] == 0:
                blk = fs._alloc_block()
                if blk > 0:
                    inode[8] = blk
                    fs._write_inode(inode_num, inode)
            fs.sys_write(fd, data)
            fs.sys_close(fd)
            loaded += 1
    return loaded
