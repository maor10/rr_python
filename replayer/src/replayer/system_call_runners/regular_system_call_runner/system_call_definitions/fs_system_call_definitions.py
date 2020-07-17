from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    create_regular_system_call_definition


read_system_call_definition = create_regular_system_call_definition(
    system_call_number=0,
    memory_address_registers=['rsi']
)


write_system_call_definition = create_regular_system_call_definition(
    system_call_number=1,
)


open_system_call_definition = create_regular_system_call_definition(
   system_call_number=2,
)


close_system_call_definition = create_regular_system_call_definition(
   system_call_number=3,
)


stat_system_call_definition = create_regular_system_call_definition(
    system_call_number=4,
    memory_address_registers=['rsi']
)


fstat_system_call_definition = create_regular_system_call_definition(
    system_call_number=5,
    memory_address_registers=['rsi']
)


lstat_system_call_definition = create_regular_system_call_definition(
    system_call_number=6,
    memory_address_registers=['rsi']
)


lseek_system_call_definition = create_regular_system_call_definition(
    system_call_number=8
)

openat_system_call_definition = create_regular_system_call_definition(
    system_call_number=257,
    memory_address_registers=['rsi']
)


