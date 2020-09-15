# The GREAT COPY TO USER WRAPPER
## General idea
After some time trying to record copy_to_user + put_user, we noticed that some syscalls call the ennoying function: `__put_user`. Since this function translates to inline assembly, we **Can't hook it**.

After some thinking, we decided to deal with these syscalls by manually recording their writes to userspace (instead of the usual approch of hooking copy_to_user).


## Implementation
In order to record every __put_user or any other inline function that writes to userspace, every function that calles __put_user must create a copy_to_user wrapper and provide a callback function 
that markes the memory that might be changed by __put_user.

The function `get_record_mem_callback` (that runs **_before_** every wrapped function) receives the set of registers that were set when function was called.
The function `get_record_mem_callback` returns the address + size of memory hooked func might write to during it's run.

The copy to user wrapper framework will copy that marked memory before every hooked func hit, and after the hooked func finishes and record all changes to that memory (since the func is the only thing that ran during that time, we can assume all memory changes were a result of the func implementation).

Using this framework, we can record memory changes made by functions calling __put_user.