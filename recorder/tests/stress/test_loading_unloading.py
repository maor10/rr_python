import pytest

REPEAT_AMOUNT = 10

@pytest.mark.parametrize("iteration", range(REPEAT_AMOUNT))
def test_crash_blast(kernel_module_context, whitelist_dmesg_context):
    with whitelist_dmesg_context(["Initializing recorder..."]):
        with kernel_module_context():
            print(f"Loaded module the {x}th time")


def test_memory_blast():
