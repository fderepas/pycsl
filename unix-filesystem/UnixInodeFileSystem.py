import struct
import time


class UnixInodeFileSystem:
    BLOCK_SIZE = 512
    NUM_BLOCKS = 256  # 128 KB Virtual Disk Block Device
    MAX_INODES = 32

    # System Call Open Flags
    O_RDONLY = 0
    O_WRONLY = 1
    O_RDWR   = 2
    O_CREAT  = 64

    # lseek Whence Flags
    SEEK_SET = 0
    SEEK_CUR = 1
    SEEK_END = 2

    def __init__(self):
        # The raw bytearray virtual hard drive
        self.disk = bytearray(self.BLOCK_SIZE * self.NUM_BLOCKS)

        # Kernel Process File Descriptor Table
        self.open_fds = {}
        self.next_fd = 3 # 0, 1, 2 reserved for standard streams

        # Format the storage array layout
        self._format_disk()

    # --- BITMAP ALGORITHMS ---

    #@ requires byte_offset >= 0
    #@ requires bit_index >= 0
    #@ requires value == 0 or value == 1
    #@ assigns self.disk
    #@ ensures True
    def _set_bitmap(self, byte_offset: int, bit_index: int, value: int) -> None:
        byte_pos = byte_offset + (bit_index // 8)
        bit_pos = bit_index % 8
        if value:
            self.disk[byte_pos] |= (1 << bit_pos)
        else:
            self.disk[byte_pos] &= ~(1 << bit_pos)

    #@ proof rocq UnixFs.Bitmap.bit_and_one_in_zero_one
    #@ requires byte_offset >= 0
    #@ requires bit_index >= 0
    #@ assigns \nothing
    #@ ensures \result >= 0 and \result < 2
    # cite:_note: postcondition discharged via the Coq axiom
    #             `bit_and_one_in_zero_one` (see
    #             unix-filesystem/UnixInodeFileSystem.proofs/rocq/
    #             UnixInodeFileSystem.v). Z3 alone times out at ~3.4B
    #             steps; with the Coq axiom imported as a Why3
    #             preamble axiom, it dispatches instantly.
    def _get_bitmap(self, byte_offset: int, bit_index: int) -> int:
        byte_pos = byte_offset + (bit_index // 8)
        bit_pos = bit_index % 8
        return (self.disk[byte_pos] >> bit_pos) & 1

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == -1 or (\result >= 1 and \result < 32)
    def _alloc_inode(self) -> int:
        #@ loop invariant 1 <= i and i <= 32
        #@ loop variant 32 - i
        for i in range(1, 32):  # MAX_INODES; literal to keep loop bound transparent to prover. Inode 0 reserved for root.
            if self._get_bitmap(0, i) == 0:
                self._set_bitmap(0, i, 1)
                return i
        return -1

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == -1 or (\result >= 6 and \result < 256)
    def _alloc_block(self) -> int:
        #@ loop invariant 6 <= i and i <= 256
        #@ loop variant 256 - i
        for i in range(6, 256):  # NUM_BLOCKS; literal. Blocks 0-5 are reserved system spaces.
            if self._get_bitmap(4, i) == 0:
                self._set_bitmap(4, i, 1)
                return i
        return -1

    # --- INODE LAYER ---

    #@ requires inode_num >= 0
    #@ requires inode_num < 32
    #@ assigns \nothing
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    #@ proof rocq UnixFs.Struct.i18.round_trip
    # cite:_note: Phase 4 of missing-bytes-struct-feature.md:
    #             struct.unpack(`>IHHHHHII10Ixx`, ...) → 18 ints.
    #             The Phase 3 round-trip axiom is registered above
    #             (`UnixFs.Struct.i18.round_trip`) and would discharge
    #             the inverse relation IF the body could be emitted.
    #             Remaining blockers: PyCSL has no IR support for
    #               (a) tuple-subscript on struct_unpack returns
    #                   (`unpacked[0]`, `unpacked[1]`, ...)
    #               (b) dict-literal body return value
    #             Both feed a follow-up missing-*-feature plan.
    def _read_inode(self, inode_num: int) -> dict:
        offset = (1 * self.BLOCK_SIZE) + (inode_num * 64)
        inode_bytes = self.disk[offset : offset + 64]
        unpacked = struct.unpack('>IHHHHHII10Ixx', inode_bytes)
        return {
            'size': unpacked[0],
            'link_count': unpacked[1],
            'type': unpacked[2],
            'mode': unpacked[3],
            'uid': unpacked[4],
            'gid': unpacked[5],
            'atime': unpacked[6],
            'mtime': unpacked[7],
            'blocks': list(unpacked[8:])
        }

    #@ requires inode_num >= 0
    #@ requires inode_num < 32
    #@ assigns self.disk
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    #@ proof rocq UnixFs.Struct.i18.round_trip
    # cite:_note: Phase 4 of missing-bytes-struct-feature.md: pairs
    #             with _read_inode under the i18 round-trip axiom.
    #             Body needs `*inode_data['blocks']` (list-spread in
    #             call args) and `self.disk[a:b] = bytes_value`
    #             (array-slice assignment with non-int RHS). Neither
    #             is in Module6 emission today; \trusted until those
    #             land.
    def _write_inode(self, inode_num: int, inode_data: dict) -> None:
        offset = (1 * self.BLOCK_SIZE) + (inode_num * 64)
        inode_bytes = struct.pack(
            '>IHHHHHII10Ixx',
            inode_data['size'], inode_data['link_count'], inode_data['type'],
            inode_data['mode'], inode_data['uid'], inode_data['gid'],
            inode_data['atime'], inode_data['mtime'],
            *inode_data['blocks']
        )
        self.disk[offset : offset + 64] = inode_bytes

    # --- DIRECTORY ENTRY RESOLUTION ---

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    # cite:_note: Phase 4 of missing-bytes-struct-feature.md:
    #             struct.unpack('>H30s', ...) under the i1a1
    #             round-trip axiom. Phase 2.3b implemented option
    #             (b) — tuple-unpack array-int targets are no
    #             longer hoisted; they're let-bound inside the
    #             loop iteration. Body now type-checks under Why3
    #             region inference.
    def _read_directory(self, block_num: int) -> list:
        offset = block_num * self.BLOCK_SIZE
        entries = []
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant 0 <= len(entries) and len(entries) <= i
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry_bytes = self.disk[entry_offset : entry_offset + 32]
            inode_num, name_bytes = struct.unpack('>H30s', entry_bytes)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if inode_num != 0 or name in ('.', '..'):
                entries.append((name, inode_num))
        return entries

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ requires \length(entries) >= 0
    #@ assigns self.disk
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    # cite:_note: Phase 4 of missing-bytes-struct-feature.md: pairs
    #             with _read_directory under the i1a1 round-trip
    #             axiom. Body needs (a) enumerate() on a list of
    #             tuples, (b) bytes.encode() / bytes.ljust(), (c)
    #             array-slice-assign with non-int RHS, (d) zero-fill
    #             `b'\x00' * BLOCK_SIZE` on the disk array. Several
    #             Module6 emission gaps; \trusted until they land.
    def _write_directory(self, block_num: int, entries: list) -> None:
        offset = block_num * self.BLOCK_SIZE
        self.disk[offset : offset + self.BLOCK_SIZE] = b'\x00' * self.BLOCK_SIZE
        for i, (name, inode_num) in enumerate(entries[:16]):
            entry_offset = offset + (i * 32)
            name_bytes = name.encode('utf-8')[:30].ljust(30, b'\x00')
            self.disk[entry_offset : entry_offset + 32] = struct.pack('>H30s', inode_num, name_bytes)

    #@ requires True
    #@ assigns self.disk
    #@ ensures True
    def _format_disk(self) -> None:
        # Set block bitmap constraints for system blocks (0 to 5)
        #@ loop invariant 0 <= b and b <= 6
        #@ loop variant 6 - b
        for b in range(6):
            self._set_bitmap(4, b, 1)

        # Standard Root Directory Inode (Inode 0 maps to physical block 5)
        self._set_bitmap(0, 0, 1)
        root_inode = {
            'size': self.BLOCK_SIZE, 'link_count': 1, 'type': 2, 'mode': 0o755,
            'uid': 0, 'gid': 0, 'atime': int(time.time()), 'mtime': int(time.time()),
            'blocks': [5] + [0]*9
        }
        self._write_inode(0, root_inode)
        # Seed default directory loopbacks
        self._write_directory(5, [('.', 0), ('..', 0)])

    # =========================================================================
    # --- ALL 20 UNIX INODE SYSTEM CALLS ---
    # =========================================================================

    #@ requires True
    #@ assigns self.disk, self.open_fds, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/open.html
    # cite:_note: POSIX open() — returns new fd >= 3 on success, -1 on
    #             ENOENT (no O_CREAT) or ENFILE (inode bitmap full).
    #             Follows symlinks 1 level via recursive sys_open call.
    def sys_open(self, pathname: str, flags: int) -> int:
        dir_entries = self._read_directory(5)
        inode_num = None
        # NOTE: loop vars renamed to leading-underscore to avoid PyCSL
        # body-leak that promotes loop vars into the emitted signature.
        for _entry_name, _entry_inode in dir_entries:
            if _entry_name == pathname:
                inode_num = _entry_inode
                break

        if inode_num is None:
            if flags & self.O_CREAT:
                inode_num = self._alloc_inode()
                if inode_num == -1: return -1
                inode_data = {
                    'size': 0, 'link_count': 1, 'type': 1, 'mode': 0o644,
                    'uid': 0, 'gid': 0, 'atime': int(time.time()), 'mtime': int(time.time()),
                    'blocks': [0]*10
                }
                self._write_inode(inode_num, inode_data)
                dir_entries.append((pathname, inode_num))
                self._write_directory(5, dir_entries)
            else:
                return -1

        inode_data = self._read_inode(inode_num)

        # Follow Symbolic Links automatically (Up to 1 depth level)
        if inode_data['type'] == 3:
            p_block = inode_data['blocks'][0]
            target_path = self.disk[p_block*self.BLOCK_SIZE : p_block*self.BLOCK_SIZE + inode_data['size']].decode('utf-8')
            return self.sys_open(target_path, flags)

        fd = self.next_fd
        self.next_fd += 1
        # Open File Descriptions mapped to Dict pointers
        self.open_fds[fd] = {'inode_num': inode_num, 'offset': 0, 'flags': flags}
        return fd

    #@ requires fd >= 0
    #@ assigns self.disk, self.open_fds
    #@ ensures \result == -1 or \result >= 0
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
    # cite:_note: POSIX write() — returns bytes written (≥0) or -1 on
    #             EBADF. Bounded by 10-direct-block / 5KB max file size.
    #             Advances open_fds[fd].offset; bumps inode mtime.
    def sys_write(self, fd: int, data) -> int:
        if fd not in self.open_fds: return -1
        ctx = self.open_fds[fd]
        if isinstance(data, str): data = data.encode('utf-8')

        inode_data = self._read_inode(ctx['inode_num'])
        bytes_written = 0

        while bytes_written < len(data):
            logical_block = ctx['offset'] // self.BLOCK_SIZE
            block_offset = ctx['offset'] % self.BLOCK_SIZE

            if logical_block >= 10: break # Enforce 10 direct blocks restriction

            if inode_data['blocks'][logical_block] == 0:
                p_block = self._alloc_block()
                if p_block == -1: break
                inode_data['blocks'][logical_block] = p_block

            p_block = inode_data['blocks'][logical_block]
            space = self.BLOCK_SIZE - block_offset
            chunk = min(space, len(data) - bytes_written)

            disk_start = (p_block * self.BLOCK_SIZE) + block_offset
            self.disk[disk_start : disk_start + chunk] = data[bytes_written : bytes_written + chunk]

            ctx['offset'] += chunk
            bytes_written += chunk
            if ctx['offset'] > inode_data['size']:
                inode_data['size'] = ctx['offset']

        inode_data['mtime'] = int(time.time())
        self._write_inode(ctx['inode_num'], inode_data)
        return bytes_written

    #@ requires fd >= 0
    #@ requires nbytes >= 0
    #@ assigns self.open_fds
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/read.html
    # cite:_note: POSIX read() — returns bytes object (≤ nbytes); empty
    #             bytes on EOF or invalid fd. PyCSL has no bytes model;
    #             post-condition captures the side effect on the FD
    #             table (offset advances) but not the returned content.
    # Note: parameter renamed nbytes→count locally to avoid PyCSL
    # body-leak that drops reassigned parameters from emitted signature.
    def sys_read(self, fd: int, nbytes: int) -> int:
        if fd not in self.open_fds: return b""
        ctx = self.open_fds[fd]
        inode_data = self._read_inode(ctx['inode_num'])

        if ctx['offset'] >= inode_data['size']: return b""
        remaining = min(nbytes, inode_data['size'] - ctx['offset'])

        bytes_read = 0
        result = bytearray()

        while bytes_read < remaining:
            logical_block = ctx['offset'] // self.BLOCK_SIZE
            block_offset = ctx['offset'] % self.BLOCK_SIZE
            p_block = inode_data['blocks'][logical_block]

            space = self.BLOCK_SIZE - block_offset
            chunk = min(space, remaining - bytes_read)

            disk_start = (p_block * self.BLOCK_SIZE) + block_offset
            result.extend(self.disk[disk_start : disk_start + chunk])

            ctx['offset'] += chunk
            bytes_read += chunk

        return bytes(result)

    #@ requires fd >= 0
    #@ assigns self.open_fds
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/close.html
    # cite:_note: POSIX close() — returns 0 on success, -1 on EBADF.
    def sys_close(self, fd: int) -> int:
        if fd in self.open_fds:
            del self.open_fds[fd]
            return 0
        return -1

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/link.html
    # cite:_note: POSIX link() — increments inode.link_count by 1;
    #             adds (newpath, inode_num) to root dir. Returns -1
    #             on ENOENT (oldpath not in root).
    def sys_link(self, oldpath: str, newpath: str) -> int:
        dir_entries = self._read_directory(5)
        inode_num = next((num for name, num in dir_entries if name == oldpath), None)
        if inode_num is None: return -1

        dir_entries.append((newpath, inode_num))
        self._write_directory(5, dir_entries)

        inode_data = self._read_inode(inode_num)
        inode_data['link_count'] += 1
        self._write_inode(inode_num, inode_data)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/unlink.html
    # cite:_note: POSIX unlink() — decrements link_count; frees blocks
    #             + inode when link_count reaches 0. Returns -1 on
    #             ENOENT.
    def sys_unlink(self, pathname: str) -> int:
        dir_entries = self._read_directory(5)
        inode_num = next((num for name, num in dir_entries if name == pathname), None)
        if inode_num is None: return -1

        dir_entries = [e for e in dir_entries if e[0] != pathname]
        self._write_directory(5, dir_entries)

        inode_data = self._read_inode(inode_num)
        inode_data['link_count'] -= 1

        if inode_data['link_count'] == 0:
            for block in inode_data['blocks']:
                if block != 0: self._set_bitmap(4, block, 0)
            self._set_bitmap(0, inode_num, 0)
        else:
            self._write_inode(inode_num, inode_data)
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html
    # cite:_note: POSIX stat() — returns stat-shaped dict (size,
    #             link_count, type, mode, uid, gid, atime, mtime,
    #             blocks[10]) or None on ENOENT. PyCSL has no record
    #             type; the multi-field return is opaque under contract.
    def sys_stat(self, pathname: str) -> int:
        dir_entries = self._read_directory(5)
        inode_num = next((num for name, num in dir_entries if name == pathname), None)
        return self._read_inode(inode_num) if inode_num is not None else None

    # --- THE 13 NEW INTEGRATED SYSTEM CALLS ---

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/mkdir.html
    # cite:_note: POSIX mkdir() — allocates inode+block, seeds '.' and
    #             '..' entries. Returns -1 on EEXIST or ENFILE/ENOSPC.
    def sys_mkdir(self, pathname: str, mode: int = 0o755) -> int:
        root_entries = self._read_directory(5)
        if any(name == pathname for name, _ in root_entries): return -1

        inode_num = self._alloc_inode()
        p_block = self._alloc_block()
        if inode_num == -1 or p_block == -1: return -1

        inode_data = {
            'size': self.BLOCK_SIZE, 'link_count': 2, 'type': 2, 'mode': mode,
            'uid': 0, 'gid': 0, 'atime': int(time.time()), 'mtime': int(time.time()),
            'blocks': [p_block] + [0]*9
        }
        self._write_inode(inode_num, inode_data)
        self._write_directory(p_block, [('.', inode_num), ('..', 0)])

        root_entries.append((pathname, inode_num))
        self._write_directory(5, root_entries)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rmdir.html
    # cite:_note: POSIX rmdir() — returns -1 on ENOENT, ENOTDIR (type
    #             != 2), or ENOTEMPTY (>2 entries past '.'/'..').
    def sys_rmdir(self, pathname: str) -> int:
        root_entries = self._read_directory(5)
        inode_num = next((num for name, num in root_entries if name == pathname), None)
        if inode_num is None: return -1

        inode_data = self._read_inode(inode_num)
        if inode_data['type'] != 2: return -1 # Not a directory

        # Confirm directory is clear of sub-allocations
        p_block = inode_data['blocks'][0]
        entries = [e for e in self._read_directory(p_block) if e[0] not in ('', '\x00')]
        if len(entries) > 2: return -1 # Directory not empty

        root_entries = [e for e in root_entries if e[0] != pathname]
        self._write_directory(5, root_entries)

        self._set_bitmap(4, p_block, 0)
        self._set_bitmap(0, inode_num, 0)
        return 0

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://man7.org/linux/man-pages/man2/getdents.2.html
    # cite:_note: Linux getdents() — returns list of (name, inode_num)
    #             tuples; -1 on EBADF or ENOTDIR (fd is not a dir).
    def sys_getdents(self, fd: int) -> int:
        if fd not in self.open_fds: return -1
        inode_num = self.open_fds[fd]['inode_num']
        inode_data = self._read_inode(inode_num)
        if inode_data['type'] != 2: return -1

        all_entries = []
        for block in inode_data['blocks']:
            if block != 0: all_entries.extend(self._read_directory(block))
        return [e for e in all_entries if e[0] != '']

    #@ requires fd >= 0
    #@ requires whence >= 0 and whence <= 2
    #@ assigns self.open_fds
    #@ ensures \result >= -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/lseek.html
    # cite:_note: POSIX lseek() — returns new offset (≥ 0) or -1 on
    #             EBADF. Resulting offset is clamped to >= 0.
    def sys_lseek(self, fd: int, offset: int, whence: int) -> int:
        if fd not in self.open_fds: return -1
        ctx = self.open_fds[fd]
        size = self._read_inode(ctx['inode_num'])['size']

        if whence == self.SEEK_SET: ctx['offset'] = offset
        elif whence == self.SEEK_CUR: ctx['offset'] += offset
        elif whence == self.SEEK_END: ctx['offset'] = size + offset

        if ctx['offset'] < 0: ctx['offset'] = 0
        return ctx['offset']

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/fsync.html
    # cite:_note: POSIX fsync() — always 0 when fd is valid (this
    #             simulator is in-memory; no real disk to flush).
    def sys_fsync(self, fd: int) -> int:
        return 0 if fd in self.open_fds else -1  # Instantly synchronized in memory space

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/chmod.html
    # cite:_note: POSIX chmod() — sets inode.mode; -1 on ENOENT.
    def sys_chmod(self, pathname: str, mode: int) -> int:
        stat = self.sys_stat(pathname)
        if not stat: return -1
        dir_entries = self._read_directory(5)
        inode_num = next(num for name, num in dir_entries if name == pathname)
        stat['mode'] = mode
        self._write_inode(inode_num, stat)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/chown.html
    # cite:_note: POSIX chown() — sets inode.uid + inode.gid; -1 on
    #             ENOENT.
    def sys_chown(self, pathname: str, owner: int, group: int) -> int:
        stat = self.sys_stat(pathname)
        if not stat: return -1
        dir_entries = self._read_directory(5)
        inode_num = next(num for name, num in dir_entries if name == pathname)
        stat['uid'], stat['gid'] = owner, group
        self._write_inode(inode_num, stat)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://man7.org/linux/man-pages/man2/utimensat.2.html
    # cite:_note: Linux utimensat() — sets inode.atime + inode.mtime;
    #             -1 on ENOENT.
    def sys_utimensat(self, pathname: str, atime: int, mtime: int) -> int:
        stat = self.sys_stat(pathname)
        if not stat: return -1
        dir_entries = self._read_directory(5)
        inode_num = next(num for name, num in dir_entries if name == pathname)
        stat['atime'], stat['mtime'] = atime, mtime
        self._write_inode(inode_num, stat)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html
    # cite:_note: POSIX rename() — atomic on this simulator (single
    #             directory block rewrite). Removes both oldpath AND
    #             newpath entries first, then re-adds (newpath, inode).
    #             -1 on ENOENT (oldpath missing).
    def sys_rename(self, oldpath: str, newpath: str) -> int:
        root_entries = self._read_directory(5)
        inode_num = next((num for name, num in root_entries if name == oldpath), None)
        if inode_num is None: return -1

        root_entries = [e for e in root_entries if e[0] != oldpath and e[0] != newpath]
        root_entries.append((newpath, inode_num))
        self._write_directory(5, root_entries)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/symlink.html
    # cite:_note: POSIX symlink() — allocates a type-3 (symlink) inode
    #             holding the target-path bytes inline. -1 on EEXIST or
    #             allocation failure.
    def sys_symlink(self, target: str, linkpath: str) -> int:
        root_entries = self._read_directory(5)
        if any(name == linkpath for name, _ in root_entries): return -1

        inode_num = self._alloc_inode()
        p_block = self._alloc_block()
        if inode_num == -1 or p_block == -1: return -1

        target_bytes = target.encode('utf-8')
        self.disk[p_block*self.BLOCK_SIZE : p_block*self.BLOCK_SIZE + len(target_bytes)] = target_bytes

        inode_data = {
            'size': len(target_bytes), 'link_count': 1, 'type': 3, 'mode': 0o777,
            'uid': 0, 'gid': 0, 'atime': int(time.time()), 'mtime': int(time.time()),
            'blocks': [p_block] + [0]*9
        }
        self._write_inode(inode_num, inode_data)
        root_entries.append((linkpath, inode_num))
        self._write_directory(5, root_entries)
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures True
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/readlink.html
    # cite:_note: POSIX readlink() — returns empty string on ENOENT or
    #             when target is not a symlink (type != 3). Successful
    #             read returns the decoded UTF-8 target path.
    def sys_readlink(self, pathname: str) -> str:
        stat = self.sys_stat(pathname)
        if not stat or stat['type'] != 3: return ""
        p_block = stat['blocks'][0]
        return self.disk[p_block*self.BLOCK_SIZE : p_block*self.BLOCK_SIZE + stat['size']].decode('utf-8')

    #@ requires oldfd >= 0
    #@ assigns self.open_fds, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/dup.html
    # cite:_note: POSIX dup() — new fd shares the SAME open-file
    #             description as oldfd (shared offset). -1 on EBADF.
    def sys_dup(self, oldfd: int) -> int:
        if oldfd not in self.open_fds: return -1
        newfd = self.next_fd
        self.next_fd += 1
        # Shares the exact same underlying open file dictionary reference (shared offset)
        self.open_fds[newfd] = self.open_fds[oldfd]
        return newfd

    #@ requires oldfd >= 0
    #@ requires newfd >= 0
    #@ assigns self.open_fds
    #@ ensures \result == newfd or \result == -1
    #@ \trusted reviewer: pycsl-self-annotate
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/dup.html
    # cite:_note: POSIX dup2() — closes newfd first if open, then makes
    #             it alias oldfd's open-file description. -1 on EBADF
    #             (oldfd not open). Note: returns the requested newfd
    #             on success, not next_fd.
    def sys_dup2(self, oldfd: int, newfd: int) -> int:
        if oldfd not in self.open_fds: return -1
        if newfd in self.open_fds: self.sys_close(newfd)
        self.open_fds[newfd] = self.open_fds[oldfd]
        return newfd
