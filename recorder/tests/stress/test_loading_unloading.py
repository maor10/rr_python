import pytest

REPEAT_AMOUNT = 10

def test_load_blast(kernel_module_context, whitelist_dmesg_context):
    for x in range(REPEAT_AMOUNT):
        with whitelist_dmesg_context(["Initializing recorder..."]), kernel_module_context():
                print(f"Loaded module the {x}th time")

