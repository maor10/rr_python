from dataclasses import dataclass


@dataclass
class Registers:
    r15: int
    r14: int
    r13: int
    r12: int
    rbp: int
    rbx: int
    r11: int
    r10: int
    r9: int
    r8: int
    rax: int
    rcx: int
    rdx: int
    rsi: int
    rdi: int
    orig_rax: int
    rip: int
    cs: int
    eflags: int
    rsp: int
    ss: int

    def to_list(self):
        return list(self.__dict__.values())

    @property
    def sys_call(self):
        return self.orig_rax

    def copy(self) -> 'Registers':
        return Registers(*self.to_list())
