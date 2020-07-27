# Replayer

The replayer is in charge of attaching to a process and putting in a "sandbox", where every sys call is answered with a pre-defined result.

The process in question must be stopped (SIGSTOP)- the replayer will attach on run and immediately send a SIGCONT signal,
and from that point on all sys calls will be sent to the replayer process.

To run the replayer:
```
from replayer import run_replayer_on_records_at_path

run_replayer_on_records_at_path(your_pid, path_to_syscall_records)
```

### How does it work?

The replayer attaches to a process with PTRACE, and then replays sys calls by replaying their memory copies (re-copying them to the given address).

The replayer does skip certain syscalls; for example, MMAP, MUNMAP, BRK.
