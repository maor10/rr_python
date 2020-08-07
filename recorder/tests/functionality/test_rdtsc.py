import hwcounter

def test_rdtsc_not_broken(kernel_module, record_syscalls_context):
    before = hwcounter.count()
    with record_syscalls_context():
        during = hwcounter.count()
    after = hwcounter.count()

    assert before < during < after, f"tick was: {during}"

def test_rdtsc_recording(kernel_module, record_syscalls_context, get_recorded_syscalls):
    with record_syscalls_context():
        hwcounter.count()
    
    a = get_recorded_syscalls()
    print(a)