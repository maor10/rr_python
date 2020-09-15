import pytest
import os

REPEAT_AMOUNT = 3

def test_load_blast(kernel_module_context, whitelist_dmesg_context, record_events_context):
    for x in range(REPEAT_AMOUNT):
        whitelist = ["Initializing recorder...", "Received command"]
        with whitelist_dmesg_context(whitelist), kernel_module_context(), record_events_context():
                print(f"Loaded module the {x}th time")