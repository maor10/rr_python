import pytest

REPEAT_AMOUNT = 10

@pytest.mark.parametrize("iteration", range(REPEAT_AMOUNT))
def test_load_blast(kernel_module_context, whitelist_dmesg_context, iteration):
    with whitelist_dmesg_context(["Initializing recorder..."]), kernel_module_context():
            print(f"Loaded module the {iteration}th time")

