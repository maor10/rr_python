from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    create_regular_system_call_definition


read_system_call_definition = create_regular_system_call_definition(
    system_call_number=0,
    memory_address_register='rsi'
)


write_system_call_definition = create_regular_system_call_definition(
    system_call_number=1,
)


open_system_call_definition = create_regular_system_call_definition(
    system_call_number=2,
)


stat_system_call_definition = create_regular_system_call_definition(
    system_call_number=3,
    memory_address_register='rdi'
)
