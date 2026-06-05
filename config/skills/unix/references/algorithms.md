# Kernel Internals Algorithms Reference
Generic kernel algorithms expressed from first principles.
The focus is cache behavior, filesystem traversal, process lifecycle, memory management, and synchronization.

## Buffer Cache Algorithms
### `buffer_lookup(device, block)`
Purpose: find whether a block is already cached; hash lookup avoids duplicate in-memory copies and unnecessary I/O.
```text
function buffer_lookup(device, block):
    for buf in hash_table[hash(device, block)]:
        if buf.device == device and buf.block == block: return buf
    return NULL
```
Key invariants / edge cases:
- At most one cached buffer should represent a given `(device, block)`.
- Lookup reports presence only; callers must still check `busy`, `valid`, and `error`.

### `buffer_get(device, block)`
Purpose: obtain an exclusive buffer; hits claim cached state, misses recycle an LRU free buffer, and callers sleep if none are free.
```text
function buffer_get(device, block):
    loop:
        buf = buffer_lookup(device, block)
        if buf != NULL:
            if buf.busy: sleep(buf.wait_queue); continue
            remove_from_free_list(buf); buf.busy = true; return buf
        if free_list.is_empty(): sleep(free_buffer_wait_queue); continue
        victim = free_list.remove_head(); victim.busy = true
        if victim.dirty: write_buffer_to_disk(victim); victim.dirty = false; victim.busy = false; buffer_release(victim); continue
        remove_from_hash(victim); victim.device = device; victim.block = block
        victim.valid = false; victim.error = false; insert_into_hash(victim); return victim
```
Key invariants / edge cases:
- Busy buffers must never remain on the free list.
- Dirty victims require write-back before reuse or data is lost.
- Sleeping callers must retry because cache state changes while they wait.

### `buffer_read(device, block)`
Purpose: return a buffer whose bytes match the requested block, issuing disk I/O only when cached contents are not already valid.
```text
function buffer_read(device, block):
    buf = buffer_get(device, block)
    if not buf.valid:
        start_disk_read(buf); sleep_until_io_completes(buf)
        if buf.io_error: buf.error = true else: buf.valid = true
    return buf
```
Key invariants / edge cases:
- `valid` means the buffer's bytes correspond to its current `(device, block)` identity.
- Concurrent readers should share one in-flight read rather than duplicating I/O.

### `buffer_release(buffer)`
Purpose: make a busy buffer reusable, restore LRU/free-list order, and wake sleepers waiting for this buffer or any free buffer.
```text
function buffer_release(buf):
    buf.busy = false
    if buf.error: free_list.insert_head(buf) else: free_list.insert_tail(buf)
    wakeup(buf.wait_queue); wakeup(free_buffer_wait_queue)
```
Key invariants / edge cases:
- Every reusable non-busy buffer should appear exactly once on the free list.
- Clear `busy` before wakeup to avoid a lost-wakeup race.

## File System Algorithms
### `inode_get(device, inode_number)`
Purpose: obtain an in-memory inode from cache or disk so open files and pathname traversal share one metadata object.
```text
function inode_get(device, inode_number):
    for inode in inode_hash[hash(device, inode_number)]:
        if inode.device == device and inode.number == inode_number: inode.refcount += 1; return inode
    if inode_free_list.is_empty(): reclaim_unused_inodes()
    inode = inode_free_list.remove_head(); remove_from_hash(inode)
    inode.device = device; inode.number = inode_number; inode.refcount = 1; inode.dirty = false
    read_inode_from_disk(inode); insert_into_hash(inode); return inode
```
Key invariants / edge cases:
- There should be at most one live in-memory inode per `(device, inode_number)`.
- A cache miss must not become visible until fields are fully initialized.

### `inode_put(inode)`
Purpose: drop an inode reference and either free its storage if unlinked or write back dirty metadata before caching it again.
```text
function inode_put(inode):
    inode.refcount -= 1
    if inode.refcount > 0: return
    if inode.link_count == 0:
        for block in inode.data_blocks: if block != NULL: free_block(block)
        free_inode_number(inode.device, inode.number); clear_inode_cache_entry(inode)
    else:
        if inode.dirty: write_inode_to_disk(inode)
        inode_free_list.insert_tail(inode)
```
Key invariants / edge cases:
- Storage is reclaimed only when both `refcount == 0` and `link_count == 0`.
- Reference counts must not underflow, even on error paths.

### `path_resolve(pathname)`
Purpose: translate a textual path into the inode of its final component by walking directories one name at a time.
```text
function path_resolve(pathname):
    inode = inode_get(root.device, root.number) if pathname.starts_with('/') else inode_get(cwd.device, cwd.number)
    for name in split_path(pathname):
        if name == '' or name == '.': continue
        if name == '..': inode = parent_of(inode)
        else:
            require_search_permission(inode); next = directory_lookup(inode, name)
            if next == NULL: inode_put(inode); return ERROR_NOT_FOUND
            inode_put(inode); inode = next
        if inode.is_mount_point_root_of_other_fs: inode = mounted_filesystem_root(inode)
    return inode
```
Key invariants / edge cases:
- Each traversed directory must permit search/execute permission.
- `.` keeps the current inode; `..` stops at the namespace root when already at root.
- Mount traversal substitutes the mounted filesystem's root inode.

### `block_alloc(filesystem)`
Purpose: allocate one free data block, preferably near related blocks to improve locality and reduce future seek or cache misses.
```text
function block_alloc(filesystem, goal_block):
    for block in scan_free_blocks(filesystem, choose_search_start(goal_block)):
        if block.is_free: mark_block_allocated(filesystem, block.number); zero_block_if_required(block.number); return block.number
    for block in scan_free_blocks(filesystem, 0):
        if block.is_free: mark_block_allocated(filesystem, block.number); zero_block_if_required(block.number); return block.number
    return ERROR_NO_SPACE
```
Key invariants / edge cases:
- Free-space metadata must never return the same block twice.
- Zeroing may be required to avoid exposing stale contents to a new file.

### `inode_alloc(filesystem)`
Purpose: allocate a fresh inode number, clear inherited state, and initialize metadata so later creation steps can safely attach it.
```text
function inode_alloc(filesystem):
    for ino in scan_inode_bitmap(filesystem):
        if inode_bitmap[ino] == FREE:
            inode_bitmap[ino] = ALLOCATED; inode = initialize_new_inode(ino)
            inode.link_count = 1; inode.size = 0; inode.data_blocks = empty_block_list()
            write_inode_to_disk(inode); return inode
    return ERROR_NO_SPACE
```
Key invariants / edge cases:
- The inode is not reachable by pathname until a directory entry points at it.
- Failed file creation must roll back inode allocation or the inode leaks.

## Process Algorithms
### `fork()`
Purpose: create a child process by cloning the caller's execution context while using copy-on-write to avoid eager memory copying.
```text
function fork():
    child = allocate_process_entry(); if child == NULL: return ERROR_NO_PROCESS_SLOT
    child.pid = allocate_pid(); child.ppid = current.pid
    child.address_space = clone_vm_as_copy_on_write(current.address_space)
    child.fd_table = copy_fd_table(current.fd_table); increment_fd_refcounts(child.fd_table)
    child.signal_handlers = copy_signal_handlers(current.signal_handlers)
    child.registers = copy_trap_frame(current.registers); child.registers.return_value = 0
    make_runnable(child); return child.pid
```
Key invariants / edge cases:
- Parent sees the child PID; child sees return value `0`.
- Copy-on-write pages must be read-only in both processes until the first write fault.

### `exec(pathname, argv, envp)`
Purpose: replace the current user program with a new executable image while keeping the same process identity in the kernel.
```text
function exec(pathname, argv, envp):
    inode = path_resolve(pathname); if inode is error: return ERROR_NOT_FOUND
    image = read_executable_headers(inode)
    if not image.is_valid_executable: inode_put(inode); return ERROR_BAD_EXECUTABLE
    destroy_user_address_space(current.address_space); current.address_space = create_empty_address_space()
    map_text_segment(current.address_space, image.text); map_data_segment(current.address_space, image.data)
    map_zero_filled_region(current.address_space, image.bss); stack = build_initial_stack(argv, envp)
    reset_caught_signals_to_default(current); clear_pending_signals(current)
    set_instruction_pointer(current, image.entry_point); set_stack_pointer(current, stack.top)
    inode_put(inode); return ENTER_USER_MODE
```
Key invariants / edge cases:
- File descriptors marked close-on-exec should be dropped during the transition.
- Loading failure must not leave a random mixture of old and new address-space state.

### `exit(status)`
Purpose: terminate a process, release resources, notify the parent, and retain exit status until the parent reaps the zombie.
```text
function exit(status):
    current.exit_status = status
    for fd in current.fd_table: if fd.is_open: close_file(fd)
    release_address_space(current.address_space)
    for child in current.children: child.ppid = init_process.pid; add_child(init_process, child)
    send_signal(current.parent, SIGCHLD)
    current.state = ZOMBIE; schedule()
```
Key invariants / edge cases:
- A zombie keeps PID and exit status but does not run user code.
- Reparenting prevents live descendants from becoming unreachable.

### `wait()`
Purpose: let a parent collect one child's termination status and free that child's process-table entry.
```text
function wait():
    loop:
        found_child = false
        for child in current.children:
            found_child = true
            if child.state == ZOMBIE: status = child.exit_status; free_process_entry(child); return status
        if not found_child: return ERROR_NO_CHILDREN
        sleep(current.child_wait_queue)
```
Key invariants / edge cases:
- Each zombie may be reaped exactly once.
- Sleep can return spuriously or due to signals, so the parent must rescan.

### `schedule()`
Purpose: choose the highest-priority runnable process, recalculate dynamic priority, and perform the mechanism of a context switch.
```text
function schedule():
    disable_preemption()
    for proc in process_table: if proc.state == RUNNABLE: proc.priority = recompute_priority(proc)
    next = highest_priority_runnable_process(); if next == NULL: next = idle_process
    if next != current:
        save_cpu_registers(current); load_address_space(next.address_space)
        load_cpu_registers(next); current = next
    enable_preemption()
```
Key invariants / edge cases:
- Only runnable tasks may be selected.
- Equal-priority tasks typically need round-robin tie breaking to avoid starvation.

## Memory Management Algorithms
### `page_fault_handler(faulting_address)`
Purpose: resolve faults by validating the address and then demand-paging, copying on write, or swapping in as needed.
```text
function page_fault_handler(addr, access_type):
    vma = find_vma(current.address_space, addr); if vma == NULL: send_signal(current, SIGSEGV); return
    pte = lookup_page_table_entry(addr)
    if pte.not_present and vma.is_demand_paged:
        frame = allocate_frame(); if vma.backed_by_file: read_page_from_file(vma.file, addr, frame) else: zero_fill(frame)
        map_page(addr, frame, vma.protection); return
    if pte.copy_on_write and access_type == WRITE:
        new_frame = allocate_frame(); copy_frame_contents(pte.frame, new_frame); decrement_frame_refcount(pte.frame)
        map_page(addr, new_frame, pte.protection + WRITE); return
    if pte.swapped_out:
        frame = allocate_frame(); read_page_from_swap(pte.swap_slot, frame); map_page(addr, frame, pte.protection); return
    send_signal(current, SIGSEGV)
```
Key invariants / edge cases:
- An address outside every VMA is a protection fault, not a recoverable demand-page event.
- Copy-on-write must preserve the original shared frame for other mappings.
- If free frames are exhausted, eviction may be needed before mapping completes.

### `page_evict()`
Purpose: reclaim a physical frame with a clock-style second-chance policy that approximates least-recently-used behavior.
```text
function page_evict():
    loop:
        page = clock_hand.current_page; clock_hand.advance()
        if page.pinned or page.busy: continue
        if page.accessed: page.accessed = false; continue
        if page.dirty: schedule_page_writeback(page); continue
        unmap_page_from_all_processes(page); remove_page_from_resident_set(page)
        free_frame_list.insert_tail(page.frame); return page.frame
```
Key invariants / edge cases:
- Pinned pages, kernel stacks, and active I/O pages may be temporarily non-evictable.
- Dirty pages must not be discarded before write-back makes their contents recoverable.

## Synchronisation Algorithms
### `spinlock_acquire(lock)`
Purpose: acquire a very short critical-section lock by repeatedly trying an atomic test-and-set without sleeping.
```text
function spinlock_acquire(lock):
    while true:
        if atomic_test_and_set(lock.state, LOCKED) == UNLOCKED:
            memory_barrier_acquire(); return
        cpu_relax()
```
Key invariants / edge cases:
- Acquisition must be atomic across CPUs.
- A thread must not sleep while holding a spinlock.

### `spinlock_release(lock)`
Purpose: release a spinlock only after protected writes are ordered before the unlock becomes visible.
```text
function spinlock_release(lock):
    memory_barrier_release()
    lock.state = UNLOCKED
```
Key invariants / edge cases:
- Release ordering prevents other CPUs from seeing partially updated protected state.
- Unlocking by a non-owner is a logic error.

### `mutex_lock(mutex)`
Purpose: acquire a sleepable mutual-exclusion lock that blocks instead of wasting CPU cycles when contested.
```text
function mutex_lock(mutex):
    loop:
        if atomic_compare_and_swap(mutex.state, UNLOCKED, LOCKED): mutex.owner = current_thread; return
        enqueue(mutex.wait_queue, current_thread)
        sleep(mutex.wait_queue)
```
Key invariants / edge cases:
- Queue insertion and sleep must be coordinated to avoid lost wakeups.
- Wakeup is only permission to retry; another thread may still win the lock first.

### `mutex_unlock(mutex)`
Purpose: release a mutex and wake one waiter so mutual exclusion continues without a thundering herd.
```text
function mutex_unlock(mutex):
    mutex.owner = NULL; mutex.state = UNLOCKED
    if not is_empty(mutex.wait_queue): wakeup(dequeue(mutex.wait_queue))
```
Key invariants / edge cases:
- Unlocking by a non-owner is a synchronization bug.
- Internal guard locking may be needed so queue updates and wakeups are atomic.

### `semaphore_wait(sem)`
Purpose: decrement a counted resource and block if demand exceeds supply.
```text
function semaphore_wait(sem):
    sem.count -= 1
    if sem.count < 0:
        enqueue(sem.wait_queue, current_thread)
        sleep(sem.wait_queue)
```
Key invariants / edge cases:
- The decrement and queueing decision must be atomic with respect to signalers.
- A negative count conceptually tracks blocked waiters.

### `semaphore_signal(sem)`
Purpose: increment a counted resource and wake one waiter when the prior count indicated blocked demand.
```text
function semaphore_signal(sem):
    sem.count += 1
    if sem.count <= 0: wakeup(dequeue(sem.wait_queue))
```
Key invariants / edge cases:
- Wake one waiter only when earlier waits drove the count to zero or below.
- Over-signaling can raise the count above intended capacity if higher-level logic is wrong.
