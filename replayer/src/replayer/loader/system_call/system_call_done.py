from dataclasses import dataclass



@dataclass
class SystemCallDone:

    ret: int

    def __repr__(self):
        return f"<{self.__class__.__name__} Ret: {self.ret}>"
