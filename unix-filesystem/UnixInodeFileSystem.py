import struct
import time


#@ class invariant \length(self.disk) >= 131072
#@ class invariant \length(self.fd_open) == 64
#@ class invariant \length(self.fd_inode) == 64
#@ class invariant \length(self.fd_offset) == 64
#@ class invariant \length(self.fd_flags) == 64
#@ class invariant self.next_fd >= 3
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

    def __init__(self, num_blocks: int = 256, load_dir=None):
        # The raw bytearray virtual hard drive (array int). Its length is the
        # disk capacity = num_blocks * BLOCK_SIZE. `num_blocks` is a runtime
        # argument so the disk can be made larger than the 256-block default;
        # it is clamped to >= 256 because the base layout (32-inode region,
        # block bitmap, root directory in block 5) and every bounds proof
        # assume at least 131072 bytes. The class invariant is
        # `\length(self.disk) >= 131072`, so a larger disk keeps every
        # access bound valid (index < 131072 <= length).
        if num_blocks < self.NUM_BLOCKS:
            num_blocks = self.NUM_BLOCKS
        self.disk: list = bytearray(num_blocks * self.BLOCK_SIZE)

        # Kernel Process File Descriptor Table. The fd table is modeled as
        # four parallel `array int` columns indexed by fd (capacity 64):
        #   fd_open[fd]   1 if fd is open, else 0 (replaces dict membership)
        #   fd_inode[fd]  inode number the fd refers to
        #   fd_offset[fd] current read/write offset
        #   fd_flags[fd]  open flags
        self.fd_open: list = [0] * 64
        self.fd_inode: list = [0] * 64
        self.fd_offset: list = [0] * 64
        self.fd_flags: list = [0] * 64
        self.next_fd = 3 # 0, 1, 2 reserved for standard streams

        # Format the storage array layout
        self._format_disk()

        # Optional: populate from a real host directory. This is a
        # runtime-only convenience — the loader performs host filesystem I/O
        # (os.walk + reading real files), which is inherently unverifiable, so
        # it lives in a separate module imported lazily here and is NOT part of
        # the verified surface. The verified syscalls do the actual writes.
        if load_dir is not None:
            from unixfs_host_loader import load_host_dir
            load_host_dir(self, load_dir)

    # --- BITMAP ALGORITHMS ---

    #@ requires byte_offset >= 0
    #@ requires bit_index >= 0
    #@ requires byte_offset + bit_index // 8 < 131072
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
    #@ proof lean UnixFs.Bitmap.bit_and_one_in_zero_one
    #@ requires byte_offset >= 0
    #@ requires bit_index >= 0
    #@ requires byte_offset + bit_index // 8 < 131072
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
    #@ ensures \length(\result) == 18
    #@ proof rocq UnixFs.Struct.i18.round_trip
    #@ proof lean UnixFs.Struct.i18.round_trip
    # cite:_note: De-trusted by the data-model rewrite
    #             (remove-trusted-unixfs.md). An inode is an 18-element
    #             `array int` in struct '>IHHHHHII10Ixx' field order:
    #               0=size 1=link_count 2=type 3=mode 4=uid 5=gid
    #               6=atime 7=mtime 8..17=blocks[0..9].
    #             Body-verified: slice-read self.disk → tuple-unpack the
    #             struct.unpack result into named locals → build the array
    #             single-exit. Round-trip discharged by the i18 axiom.
    def _read_inode(self, inode_num: int) -> list:
        offset = 512 + (inode_num * 64)
        inode_bytes = self.disk[offset:offset + 64]
        (f0, f1, f2, f3, f4, f5, f6, f7, f8, f9,
         f10, f11, f12, f13, f14, f15, f16, f17) = struct.unpack('>IHHHHHII10Ixx', inode_bytes)
        inode = [f0, f1, f2, f3, f4, f5, f6, f7, f8, f9,
                 f10, f11, f12, f13, f14, f15, f16, f17]
        return inode

    #@ requires inode_num >= 0
    #@ requires inode_num < 32
    #@ requires \length(inode) == 18
    #@ assigns self.disk
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i18.round_trip
    #@ proof lean UnixFs.Struct.i18.round_trip
    # cite:_note: De-trusted by the data-model rewrite. Pairs with
    #             _read_inode under the i18 round-trip axiom. The inode
    #             array is packed with 18 explicit positional args (no
    #             *spread) and blitted into the disk field via
    #             `self.disk[a:b] = packed` (Array.blit). `requires
    #             \length(inode) == 18` is a memory-safety precondition
    #             for the 18 element reads.
    def _write_inode(self, inode_num: int, inode: list) -> None:
        offset = 512 + (inode_num * 64)
        inode_bytes = struct.pack(
            '>IHHHHHII10Ixx',
            inode[0], inode[1], inode[2], inode[3], inode[4], inode[5],
            inode[6], inode[7], inode[8], inode[9], inode[10], inode[11],
            inode[12], inode[13], inode[14], inode[15], inode[16], inode[17])
        self.disk[offset:offset + 64] = inode_bytes

    #@ requires block >= 6 and block < 256
    #@ assigns self.disk
    #@ raises ValueError when \length(data) > 512
    #@ ensures \array_eq(\result, data)
    # cite:_note: Verified byte round-trip — the model-level analog of
    #             "write a string then read it back unchanged" (cf. my_os
    #             / my_os_demo, which stay runtime-only). Writes `data`
    #             into data block `block` and reads it back; proves that
    #             it either raises ValueError (size error — PyCSL has no
    #             OSError) or returns an array extensionally equal to
    #             `data`. Pure Why3: the write is `Array.blit` (disk[a+i]
    #             = data[i]) and the read-back slice is `Array.sub`
    #             (result[i] = disk[a+i]), so result[i] = data[i]. `data`
    #             is universally quantified — stronger than one value.
    #             Does NOT cover the cross-syscall open/write/close/open/
    #             read path (intervening abstract calls havoc the disk;
    #             reopen-by-name needs an unmodeled string lookup).
    def _block_roundtrip(self, block: int, data: list) -> list:
        n = len(data)
        if n > 512:
            raise ValueError
        start = block * 512
        self.disk[start:start + n] = data
        return self.disk[start:start + n]

    # --- DIRECTORY ENTRY RESOLUTION ---

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    #@ proof lean UnixFs.Struct.i1a1.round_trip
    # cite:_note: Phase 4 of missing-bytes-struct-feature.md:
    #             struct.unpack('>H30s', ...) under the i1a1
    #             round-trip axiom. Phase 2.3b implemented option
    #             (b) — tuple-unpack array-int targets are no
    #             longer hoisted; they're let-bound inside the
    #             loop iteration. Body now type-checks under Why3
    #             region inference.
    def _read_directory(self, block_num: int) -> list:
        offset = block_num * 512  # literal (self.BLOCK_SIZE is opaque to the prover)
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
    #@ requires \length(inodes) == 16
    #@ requires \length(names) == 480
    #@ assigns self.disk
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    #@ proof lean UnixFs.Struct.i1a1.round_trip
    # cite:_note: De-trusted by the data-model rewrite
    #             (remove-trusted-unixfs.md). A directory block holds 16
    #             entries of struct '>H30s' (inode_num : H, name : 30-byte
    #             field). Entries are passed as parallel int arrays —
    #             `inodes` (16 inode numbers) and `names` (a flat
    #             16*30 = 480-byte name buffer; entry i's name is
    #             names[i*30 : i*30+30]). This replaces the original
    #             list-of-(str,int)-tuples + enumerate + bytes.encode/
    #             ljust, none of which PyCSL can emit. The block is
    #             zero-filled then each entry packed (i1a1) and blitted
    #             in one bounded range(16) loop.
    def _write_directory(self, block_num: int, inodes: list, names: list) -> None:
        offset = block_num * 512
        self.disk[offset:offset + 512] = b'\x00' * 512
        #@ loop invariant 0 <= i and i <= 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            name_slice = names[i * 30:i * 30 + 30]
            self.disk[entry_offset:entry_offset + 32] = struct.pack('>H30s', inodes[i], name_slice)

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    #@ proof lean UnixFs.Struct.i1a1.round_trip
    # cite:_note: Reusable directory name-lookup for the path-based
    #             syscalls. Scans the 16 entries of a directory block,
    #             decodes each name, and returns the inode number whose
    #             name equals `pathname` (or -1). The scan (loop bounds,
    #             i1a1 unpack, running `found`) is body-verified. `pathname`
    #             is a real Why3 string, but `name` comes from `.decode()` of
    #             on-disk bytes — the opaque bytes<->str codec boundary — so
    #             the `name == pathname` compare reverts to opaque
    #             hash-identity (str_hash_op), not content equality. (PyCSL
    #             has a string model now; only the .decode/.encode codec is
    #             opaque.) Same shape as in _read_directory.
    def _dir_lookup(self, block_num: int, pathname: str) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = struct.unpack('>H30s', entry)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if name == pathname and inode_num != 0:
                found = inode_num
        return found

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures \result >= -1 and \result < 16
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    #@ proof lean UnixFs.Struct.i1a1.round_trip
    # cite:_note: Returns the entry SLOT index (0..15) whose name equals
    #             `pathname`, or -1. Companion of _dir_lookup (which
    #             returns the inode); the bounded slot lets callers
    #             zero / overwrite a specific 32-byte entry in bounds.
    def _dir_find_slot(self, block_num: int, pathname: str) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant found >= -1 and found < 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = struct.unpack('>H30s', entry)
            name = name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')
            if name == pathname and inode_num != 0:
                found = i
        return found

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ assigns \nothing
    #@ ensures \result >= -1 and \result < 16
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    #@ proof lean UnixFs.Struct.i1a1.round_trip
    # cite:_note: Returns a free entry SLOT index (0..15, inode_num == 0)
    #             or -1 if the directory block is full.
    def _dir_find_free(self, block_num: int) -> int:
        offset = block_num * 512
        found = -1
        #@ loop invariant 0 <= i and i <= 16
        #@ loop invariant found >= -1 and found < 16
        #@ loop variant 16 - i
        for i in range(16):
            entry_offset = offset + (i * 32)
            entry = self.disk[entry_offset:entry_offset + 32]
            inode_num, name_bytes = struct.unpack('>H30s', entry)
            if inode_num == 0:
                found = i
        return found

    #@ requires block_num >= 0
    #@ requires block_num < 256
    #@ requires slot >= 0 and slot < 16
    #@ assigns self.disk
    #@ ensures True
    #@ proof rocq UnixFs.Struct.i1a1.round_trip
    #@ proof lean UnixFs.Struct.i1a1.round_trip
    # cite:_note: Writes a single 32-byte directory entry (struct '>H30s')
    #             at `slot` of `block_num`. The name is `name.encode(...)`
    #             — an opaque byte buffer: `name: str` is a real Why3 string,
    #             but `.encode()` is the opaque str->bytes codec boundary, so
    #             the encoded content is not value-modeled (the pack/blit is
    #             still body-verified).
    def _write_entry(self, block_num: int, slot: int, inode_num: int, name: str) -> None:
        entry_offset = block_num * 512 + slot * 32
        self.disk[entry_offset:entry_offset + 32] = struct.pack('>H30s', inode_num, name.encode('utf-8'))

    #@ requires True
    #@ assigns self.disk
    #@ ensures True
    def _format_disk(self) -> None:
        # Set block bitmap constraints for system blocks (0 to 5)
        #@ loop invariant 0 <= b and b <= 6
        #@ loop variant 6 - b
        for b in range(6):
            self._set_bitmap(4, b, 1)

        # Standard Root Directory Inode (Inode 0 maps to physical block 5).
        # Inode is the 18-element array model (see _read_inode field map):
        # size=512, link_count=1, type=2 (dir), mode=0o755 (493), uid/gid=0,
        # atime/mtime=0 (real-clock seeding dropped under the int-array
        # rewrite — not constrained by the contract), blocks=[5,0*9].
        self._set_bitmap(0, 0, 1)
        root_inode = [512, 1, 2, 493, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._write_inode(0, root_inode)
        # Seed the '.' and '..' loopback entries in directory block 5 via the
        # shared _write_entry helper, so the names are encoded as real bytes
        # (`name.encode('utf-8')`) — both body-verified and runtime-correct
        # (a raw int-list would break struct '30s' at Python runtime).
        self._write_entry(5, 0, 0, ".")
        self._write_entry(5, 1, 0, "..")

    # =========================================================================
    # --- ALL 20 UNIX INODE SYSTEM CALLS ---
    # =========================================================================

    #@ requires True
    #@ assigns self.disk, self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/open.html
    # cite:_note: POSIX open() — returns a new fd >= 3 on success, -1 on
    #             ENOENT (no O_CREAT), ENFILE (inode bitmap full), or a
    #             full fd table / full root dir. De-trusted: name lookup
    #             via _dir_lookup; on O_CREAT a fresh type-1 file inode
    #             (mode 0o644=420) is allocated + linked; the new fd takes
    #             the next parallel-array slot. The original's 1-level
    #             symlink-follow (recurse on the decoded target string) is
    #             dropped — the target is decoded from bytes through the
    #             opaque codec boundary, so its content can't be followed.
    #             next_fd>=3 invariant gives \result >= 3.
    def sys_open(self, pathname: str, flags: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0:
            if flags & 64 != 0:
                inode_num = self._alloc_inode()
                if inode_num < 0 or inode_num >= 32:
                    return -1
                inode = [0, 1, 1, 420, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self._write_inode(inode_num, inode)
                slot = self._dir_find_free(5)
                if slot < 0:
                    return -1
                self._write_entry(5, slot, inode_num, pathname)
            else:
                return -1
        if inode_num < 0 or inode_num >= 32:
            return -1
        fd = self.next_fd
        if fd < 0 or fd >= 64:
            return -1
        self.next_fd = fd + 1
        self.fd_open[fd] = 1
        self.fd_inode[fd] = inode_num
        self.fd_offset[fd] = 0
        self.fd_flags[fd] = flags
        return fd

    #@ requires fd >= 0
    #@ requires \length(data) <= 512
    #@ assigns self.disk, self.fd_offset
    #@ ensures \result == -1 or \result >= 0
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/write.html
    # cite:_note: POSIX write() — returns bytes written (>= 0) or -1 on
    #             EBADF. De-trusted: `data` is an `array int` byte buffer;
    #             the bytes are blitted into the file's first direct block
    #             (index 8). The original's multi-block (10-direct-block /
    #             5KB) loop is simplified to a single bounded block write
    #             (`requires \length(data) <= 512`) — a documented
    #             capacity reduction, the contract (>=0 / -1) is preserved.
    def sys_write(self, fd: int, data: list) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        p_block = inode[8]
        if p_block <= 0 or p_block >= 256:
            return -1
        n = len(data)
        disk_start = p_block * 512
        self.disk[disk_start:disk_start + n] = data
        self.fd_offset[fd] = self.fd_offset[fd] + n
        if n > inode[0]:
            inode[0] = n
            self._write_inode(inode_num, inode)
        return n

    #@ requires fd >= 0
    #@ requires nbytes >= 0
    #@ assigns self.fd_offset
    #@ ensures True
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/read.html
    # cite:_note: POSIX read() — the original returned a bytes object
    #             (<= nbytes); PyCSL has no bytes-return model, so under
    #             `ensures True` this de-trusted form advances the fd
    #             offset by the clamped count and returns that count
    #             (>= 0) or -1 on EBADF. Return-shape change; the FD-table
    #             side effect (offset advance) is preserved.
    def sys_read(self, fd: int, nbytes: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        size = inode[0]
        avail = size - self.fd_offset[fd]
        if avail < 0:
            avail = 0
        n = nbytes
        if n > avail:
            n = avail
        self.fd_offset[fd] = self.fd_offset[fd] + n
        return n

    #@ requires fd >= 0
    #@ assigns self.fd_open
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/close.html
    # cite:_note: POSIX close() — returns 0 on success, -1 on EBADF.
    #             De-trusted: dict membership → fd_open[fd]==1, `del` →
    #             fd_open[fd]=0. The `fd < 64` guard short-circuits the
    #             array read so the access is in-bounds.
    def sys_close(self, fd: int) -> int:
        if fd < 64 and self.fd_open[fd] == 1:
            self.fd_open[fd] = 0
            return 0
        return -1

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/link.html
    # cite:_note: POSIX link() — increments inode.link_count (index 1) by
    #             1; adds a (newpath, inode_num) entry to the root dir.
    #             -1 on ENOENT or a full root dir. De-trusted: lookup →
    #             free-slot → write entry → bump link_count.
    def sys_link(self, oldpath: str, newpath: str) -> int:
        inode_num = self._dir_lookup(5, oldpath)
        if inode_num < 0 or inode_num >= 32:
            return -1
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        self._write_entry(5, slot, inode_num, newpath)
        inode = self._read_inode(inode_num)
        inode[1] = inode[1] + 1
        self._write_inode(inode_num, inode)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/unlink.html
    # cite:_note: POSIX unlink() — decrements link_count (index 1); frees
    #             the 10 direct blocks (indices 8..17) + the inode bitmap
    #             when it reaches 0. -1 on ENOENT. De-trusted: lookup →
    #             zero the entry slot → decrement → free.
    def sys_unlink(self, pathname: str) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        slot = self._dir_find_slot(5, pathname)
        if slot >= 0:
            self.disk[2560 + slot * 32:2560 + slot * 32 + 32] = b'\x00' * 32
        inode = self._read_inode(inode_num)
        inode[1] = inode[1] - 1
        if inode[1] == 0:
            #@ loop invariant 8 <= k and k <= 18
            #@ loop variant 18 - k
            for k in range(8, 18):
                block = inode[k]
                if block > 0 and block < 256:
                    self._set_bitmap(4, block, 0)
            self._set_bitmap(0, inode_num, 0)
        else:
            self._write_inode(inode_num, inode)
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures True
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/stat.html
    # cite:_note: POSIX stat() — locates the inode for `pathname` in the
    #             root directory. De-trusted: name lookup via _dir_lookup;
    #             the original returned a stat-shaped dict (PyCSL has no
    #             record type), so under `ensures True` this returns the
    #             inode number (>= 0) or -1 on ENOENT — a documented
    #             return-shape change, not contract-constrained.
    def sys_stat(self, pathname: str) -> int:
        return self._dir_lookup(5, pathname)

    # --- THE 13 NEW INTEGRATED SYSTEM CALLS ---

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/mkdir.html
    # cite:_note: POSIX mkdir() — allocates inode+block, seeds '.' and
    #             '..', and links the dir into the root. -1 on EEXIST or
    #             ENFILE/ENOSPC / full root. De-trusted: array inode +
    #             byte-level entry writes (atime/mtime seeded 0).
    def sys_mkdir(self, pathname: str, mode: int) -> int:
        if self._dir_lookup(5, pathname) >= 0:
            return -1
        inode_num = self._alloc_inode()
        if inode_num < 0 or inode_num >= 32:
            return -1
        p_block = self._alloc_block()
        if p_block < 0 or p_block >= 256:
            return -1
        inode = [512, 2, 2, mode, 0, 0, 0, 0, p_block, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._write_inode(inode_num, inode)
        self._write_entry(p_block, 0, inode_num, ".")
        self._write_entry(p_block, 1, 0, "..")
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        self._write_entry(5, slot, inode_num, pathname)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rmdir.html
    # cite:_note: POSIX rmdir() — -1 on ENOENT or ENOTDIR (type at index
    #             2 != 2). De-trusted: lookup → type check → zero the root
    #             entry → free the dir's data block + inode. (The original
    #             ENOTEMPTY check required scanning the child dir for live
    #             names — a string operation; dropped under `ensures
    #             0/-1`, a documented behaviour change.)
    def sys_rmdir(self, pathname: str) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if inode[2] != 2:
            return -1
        slot = self._dir_find_slot(5, pathname)
        if slot >= 0:
            self.disk[2560 + slot * 32:2560 + slot * 32 + 32] = b'\x00' * 32
        p_block = inode[8]
        if p_block > 0 and p_block < 256:
            self._set_bitmap(4, p_block, 0)
        self._set_bitmap(0, inode_num, 0)
        return 0

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures True
    # cite: https://man7.org/linux/man-pages/man2/getdents.2.html
    # cite:_note: Linux getdents() — the original returned a list of
    #             (name, inode_num) tuples (no list/tuple/string return
    #             model in PyCSL). De-trusted under `ensures True`: checks
    #             fd validity + that the inode is a directory (type index
    #             2 == 2) and returns 0 / -1. Return-shape change.
    def sys_getdents(self, fd: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        inode_num = self.fd_inode[fd]
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if inode[2] != 2:
            return -1
        return 0

    #@ requires fd >= 0
    #@ requires whence >= 0 and whence <= 2
    #@ assigns self.fd_offset
    #@ ensures \result >= -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/lseek.html
    # cite:_note: POSIX lseek() — returns new offset (≥ 0) or -1 on
    #             EBADF. Resulting offset is clamped to >= 0. De-trusted:
    #             fd context → fd_offset[fd] / fd_inode[fd]; whence
    #             literals 0/1/2 (SEEK_SET/CUR/END). The inode read for
    #             SEEK_END is guarded so _read_inode's 0<=n<32 precondition
    #             holds.
    def sys_lseek(self, fd: int, offset: int, whence: int) -> int:
        if fd >= 64:
            return -1
        if self.fd_open[fd] == 0:
            return -1
        if whence == 0:
            self.fd_offset[fd] = offset
        elif whence == 1:
            self.fd_offset[fd] = self.fd_offset[fd] + offset
        elif whence == 2:
            inode_num = self.fd_inode[fd]
            if inode_num >= 0 and inode_num < 32:
                inode = self._read_inode(inode_num)
                self.fd_offset[fd] = inode[0] + offset
        if self.fd_offset[fd] < 0:
            self.fd_offset[fd] = 0
        return self.fd_offset[fd]

    #@ requires fd >= 0
    #@ assigns \nothing
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/fsync.html
    # cite:_note: POSIX fsync() — always 0 when fd is valid (this
    #             simulator is in-memory; no real disk to flush).
    #             De-trusted: dict membership → fd_open[fd]==1.
    def sys_fsync(self, fd: int) -> int:
        if fd < 64 and self.fd_open[fd] == 1:
            return 0
        return -1

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/chmod.html
    # cite:_note: POSIX chmod() — sets inode.mode (array index 3); -1 on
    #             ENOENT. De-trusted: lookup → read 18-int inode → set
    #             field → write back.
    def sys_chmod(self, pathname: str, mode: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        inode[3] = mode
        self._write_inode(inode_num, inode)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/chown.html
    # cite:_note: POSIX chown() — sets inode.uid (4) + inode.gid (5); -1
    #             on ENOENT. De-trusted.
    def sys_chown(self, pathname: str, owner: int, group: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        inode[4] = owner
        inode[5] = group
        self._write_inode(inode_num, inode)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://man7.org/linux/man-pages/man2/utimensat.2.html
    # cite:_note: Linux utimensat() — sets inode.atime (6) + inode.mtime
    #             (7); -1 on ENOENT. De-trusted.
    def sys_utimensat(self, pathname: str, atime: int, mtime: int) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        inode[6] = atime
        inode[7] = mtime
        self._write_inode(inode_num, inode)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/rename.html
    # cite:_note: POSIX rename() — removes both the oldpath and any
    #             existing newpath entry, then writes (newpath, inode) in
    #             a free slot. -1 on ENOENT (oldpath missing) / full dir.
    #             De-trusted: lookup → zero old slot → zero any newpath
    #             slot → write the new entry.
    def sys_rename(self, oldpath: str, newpath: str) -> int:
        inode_num = self._dir_lookup(5, oldpath)
        if inode_num < 0 or inode_num >= 32:
            return -1
        old_slot = self._dir_find_slot(5, oldpath)
        if old_slot >= 0:
            self.disk[2560 + old_slot * 32:2560 + old_slot * 32 + 32] = b'\x00' * 32
        new_slot = self._dir_find_slot(5, newpath)
        if new_slot >= 0:
            self.disk[2560 + new_slot * 32:2560 + new_slot * 32 + 32] = b'\x00' * 32
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        self._write_entry(5, slot, inode_num, newpath)
        return 0

    #@ requires True
    #@ assigns self.disk
    #@ ensures \result == 0 or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/symlink.html
    # cite:_note: POSIX symlink() — allocates a type-3 (symlink) inode
    #             holding the target-path bytes inline in its data block.
    #             -1 on EEXIST or allocation failure / full dir.
    #             De-trusted: the target bytes are written via a '>H30s'
    #             pack of `target.encode(...)` (opaque buffer, gap 5);
    #             size field set to 30 (the on-disk name-field width).
    def sys_symlink(self, target: str, linkpath: str) -> int:
        if self._dir_lookup(5, linkpath) >= 0:
            return -1
        inode_num = self._alloc_inode()
        if inode_num < 0 or inode_num >= 32:
            return -1
        p_block = self._alloc_block()
        if p_block < 0 or p_block >= 256:
            return -1
        self.disk[p_block * 512:p_block * 512 + 32] = struct.pack('>H30s', 0, target.encode('utf-8'))
        inode = [30, 1, 3, 511, 0, 0, 0, 0, p_block, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._write_inode(inode_num, inode)
        slot = self._dir_find_free(5)
        if slot < 0:
            return -1
        self._write_entry(5, slot, inode_num, linkpath)
        return 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures True
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/readlink.html
    # cite:_note: POSIX readlink() — the original returned the decoded
    #             UTF-8 target path; that decode crosses the opaque
    #             bytes<->str codec boundary (the target is stored as bytes),
    #             so under `ensures True` this de-trusted form returns the symlink
    #             inode's first data block (index 8 — where the target
    #             bytes are stored), or -1 on ENOENT / non-symlink
    #             (type at index 2 != 3). Return-shape change, not
    #             contract-constrained.
    def sys_readlink(self, pathname: str) -> int:
        inode_num = self._dir_lookup(5, pathname)
        if inode_num < 0 or inode_num >= 32:
            return -1
        inode = self._read_inode(inode_num)
        if inode[2] != 3:
            return -1
        return inode[8]

    #@ requires oldfd >= 0
    #@ assigns self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.next_fd
    #@ ensures \result == -1 or \result >= 3
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/dup.html
    # cite:_note: POSIX dup() — -1 on EBADF or when the fd table is full
    #             (next_fd >= 64). De-trusted: the new fd's four columns
    #             are value-copied from oldfd's (the original shared the
    #             dict reference for a shared offset; the parallel-array
    #             model copies values — a documented behaviour change, not
    #             constrained by the contract). next_fd >= 3 invariant
    #             gives \result >= 3.
    def sys_dup(self, oldfd: int) -> int:
        if oldfd >= 64 or self.fd_open[oldfd] == 0:
            return -1
        newfd = self.next_fd
        if newfd >= 64:
            return -1
        self.next_fd = newfd + 1
        self.fd_open[newfd] = 1
        self.fd_inode[newfd] = self.fd_inode[oldfd]
        self.fd_offset[newfd] = self.fd_offset[oldfd]
        self.fd_flags[newfd] = self.fd_flags[oldfd]
        return newfd

    #@ requires oldfd >= 0
    #@ requires newfd >= 0
    #@ assigns self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags
    #@ ensures \result == newfd or \result == -1
    # cite: https://pubs.opengroup.org/onlinepubs/9699919799/functions/dup.html
    # cite:_note: POSIX dup2() — closes newfd first if open, then makes it
    #             alias oldfd. Returns the requested newfd on success, -1
    #             on EBADF (oldfd not open / newfd out of range).
    #             De-trusted: the four fd columns are value-copied (see
    #             sys_dup note). The inline overwrite subsumes the close.
    def sys_dup2(self, oldfd: int, newfd: int) -> int:
        if oldfd >= 64 or self.fd_open[oldfd] == 0:
            return -1
        if newfd >= 64:
            return -1
        self.fd_open[newfd] = 1
        self.fd_inode[newfd] = self.fd_inode[oldfd]
        self.fd_offset[newfd] = self.fd_offset[oldfd]
        self.fd_flags[newfd] = self.fd_flags[oldfd]
        return newfd
