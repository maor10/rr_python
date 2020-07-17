from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    create_regular_system_call_definition


gettimeofday_system_call_definition = create_regular_system_call_definition(
    system_call_number=96,
    memory_address_registers=['rdi', 'rsi']
)


sysinfo_system_call_definition = create_regular_system_call_definition(
    system_call_number=99,
    memory_address_registers=['rdi']
)


clock_gettime_system_call_definition = create_regular_system_call_definition(
    system_call_number=228,
    memory_address_registers=['rsi']
)


getrandom_system_call_definition = create_regular_system_call_definition(
    system_call_number=318,
    memory_address_registers=['rdi']
)