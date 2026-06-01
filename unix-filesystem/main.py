from  UnixInodeFileSystem import UnixInodeFileSystem

if __name__ == "__main__":
    fs = UnixInodeFileSystem()

    print("=== 1. Testing Metadata Modifications (chmod, chown, utimensat) ===")
    fs.sys_open("document.txt", fs.O_CREAT | fs.O_RDWR)
    fs.sys_chmod("document.txt", 0o777)
    fs.sys_chown("document.txt", 501, 20)
    fs.sys_utimensat("document.txt", 11111, 22222)
    
    stat = fs.sys_stat("document.txt")
    print(f"Mode: {oct(stat['mode'])}, UID: {stat['uid']}, Mtime: {stat['mtime']}\n")

    print("=== 2. Testing Path Link Transitions (symlink, readlink, rename) ===")
    fs.sys_symlink("document.txt", "shortcut.lnk")
    print(f"Symlink points to target path string: '{fs.sys_readlink('shortcut.lnk')}'")
    fs.sys_rename("document.txt", "archive.txt")
    print(f"Stat on old name: {fs.sys_stat('document.txt')} | Stat on new name size: {fs.sys_stat('archive.txt')['size']}\n")

    print("=== 3. Testing Directory Nodes (mkdir, getdents, rmdir) ===")
    fs.sys_mkdir("home_dir")
    dir_fd = fs.sys_open("home_dir", fs.O_RDONLY)
    print(f"Directory Contents Listing: {fs.sys_getdents(dir_fd)}")
    fs.sys_close(dir_fd)
    fs.sys_rmdir("home_dir")
    print(f"Directory stat post-rmdir: {fs.sys_stat('home_dir')}\n")

    print("=== 4. Testing Core Process Descriptor Replication (dup, dup2, lseek) ===")
    fd_orig = fs.sys_open("archive.txt", fs.O_CREAT | fs.O_RDWR)
    fs.sys_write(fd_orig, "Shared state string testing sequence.")
    
    fd_dup = fs.sys_dup(fd_orig)
    print(f"Original FD: {fd_orig}, Duplicated FD: {fd_dup}")
    
    fs.sys_lseek(fd_orig, 7, fs.SEEK_SET)
    print(f"Duplicated offset shifted automatically via shared state tracking: {fs.open_fds[fd_dup]['offset']}")
    print(f"Read from duplicated descriptor: {fs.sys_read(fd_dup, 5).decode('utf-8')}")
    
    fs.sys_fsync(fd_orig)
    print("Fsync finished execution successfully.\n")

    print("=== 5. Testing Hard Links, Unlink, and dup2 (sys_link, sys_unlink, sys_dup2) ===")
    fs.sys_link("archive.txt", "backup.txt")
    stat_link = fs.sys_stat("backup.txt")
    print(f"Hard link created — link_count: {stat_link['link_count']}")

    fs.sys_unlink("archive.txt")
    print(f"Unlinked 'archive.txt' — stat: {fs.sys_stat('archive.txt')}")
    stat_backup = fs.sys_stat("backup.txt")
    print(f"'backup.txt' survives — link_count: {stat_backup['link_count']}, size: {stat_backup['size']}")

    fd_backup = fs.sys_open("backup.txt", fs.O_RDWR)
    fd_target = 10
    fd_result = fs.sys_dup2(fd_backup, fd_target)
    print(f"dup2({fd_backup}, {fd_target}) returned: {fd_result}")
    fs.sys_lseek(fd_target, 0, fs.SEEK_SET)
    print(f"Read via dup2 descriptor: {fs.sys_read(fd_target, 6).decode('utf-8')}\n")

    print("=== 6a. Testing Error Cases — Invalid File Descriptor (read, write, close, lseek, fsync, getdents, dup, dup2) ===")
    bad_fd = 999
    print(f"  read(bad_fd):     {fs.sys_read(bad_fd, 10)}")
    print(f"  write(bad_fd):    {fs.sys_write(bad_fd, 'data')}")
    print(f"  close(bad_fd):    {fs.sys_close(bad_fd)}")
    print(f"  lseek(bad_fd):    {fs.sys_lseek(bad_fd, 0, fs.SEEK_SET)}")
    print(f"  fsync(bad_fd):    {fs.sys_fsync(bad_fd)}")
    print(f"  getdents(bad_fd): {fs.sys_getdents(bad_fd)}")
    print(f"  dup(bad_fd):      {fs.sys_dup(bad_fd)}")
    print(f"  dup2(bad_fd, 20): {fs.sys_dup2(bad_fd, 20)}")

    print("=== 6b. Testing Error Cases — Nonexistent Path (open, stat, link, unlink, chmod, chown, utimensat, rename, readlink) ===")
    ghost = "no_such_file.txt"
    print(f"  open(ghost, RDONLY): {fs.sys_open(ghost, fs.O_RDONLY)}")
    print(f"  stat(ghost):         {fs.sys_stat(ghost)}")
    print(f"  link(ghost, x):      {fs.sys_link(ghost, 'x')}")
    print(f"  unlink(ghost):       {fs.sys_unlink(ghost)}")
    print(f"  chmod(ghost):        {fs.sys_chmod(ghost, 0o644)}")
    print(f"  chown(ghost):        {fs.sys_chown(ghost, 0, 0)}")
    print(f"  utimensat(ghost):    {fs.sys_utimensat(ghost, 0, 0)}")
    print(f"  rename(ghost):       {fs.sys_rename(ghost, 'other')}")
    print(f"  readlink(ghost):     '{fs.sys_readlink(ghost)}'")

    print("=== 6c. Testing Error Cases — Directory-Specific (mkdir, rmdir, getdents, symlink, readlink) ===")
    fs.sys_mkdir("testdir")
    print(f"  mkdir(duplicate):     {fs.sys_mkdir('testdir')}")

    # Create a file inside testdir to test non-empty rmdir
    inner_fd = fs.sys_open("inner.txt", fs.O_CREAT | fs.O_RDWR)
    fs.sys_close(inner_fd)
    print(f"  rmdir(file):          {fs.sys_rmdir('inner.txt')}")

    # getdents on a regular file fd
    file_fd = fs.sys_open("backup.txt", fs.O_RDONLY)
    print(f"  getdents(file_fd):    {fs.sys_getdents(file_fd)}")
    fs.sys_close(file_fd)

    # symlink with existing name
    print(f"  symlink(dup name):    {fs.sys_symlink('x', 'backup.txt')}")

    # readlink on a regular file (not a symlink)
    print(f"  readlink(reg file):   '{fs.sys_readlink('backup.txt')}'")

    # rmdir nonexistent
    print(f"  rmdir(ghost):         {fs.sys_rmdir(ghost)}")

    # Cleanup
    fs.sys_rmdir("testdir")
    fs.sys_unlink("inner.txt")
    print("All error cases returned expected values.")
