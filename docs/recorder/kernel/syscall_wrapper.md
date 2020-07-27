# The GREAT SYSCALL WRAPPER
## General idea
After some time trying to record copy_to_user + put_user, we noticed that some syscalls call the ennoying function: `__put_user`. Since this function translates to inline assembly, we **Can't hook it**.

After some thinking, we decided to deal with these syscalls by manually recording their writes to userspace (instead of the usual approch of hooking copy_to_user).


## Implementation
In order to record every wrapped syscall, every syscall wrapper must implement a callback function that markes the memory that might be changed by the syscall.

The function `get_record_mem_callback` (that runs **_before_** every syscall) receives the set of registers that were set when syscall was called.
The function returns the address + size of memory syscall might write to during it's run.

The syscall wrapper framework will copy that marked memory before every syscall hit, and after the syscall finishes and record all changes to that memory (since the syscall is the only thing that ran during that time, we can assume all memory changes were a result of the syscall implementation).

Using this framework, we can record memory changes made by syscalls calling __put_user.