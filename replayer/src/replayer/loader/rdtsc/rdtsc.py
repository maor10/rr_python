from dataclasses import dataclass

RDTSC_EVENT_ID = 0

@dataclass
class Rdtsc:
    ax: int
    dx: int