from replayer.system_call_runners.regular_system_call_runner.regular_system_call_definition import \
    create_regular_system_call_definition


poll_system_call_definition = create_regular_system_call_definition(
    system_call_number=7,
    memory_address_registers=["rdi"]
)


select_system_call_definition = create_regular_system_call_definition(
    system_call_number=23,
    memory_address_registers=["rsi", "rdx", "r10"]
)


socket_system_call_definition = create_regular_system_call_definition(
    system_call_number=41,
)


connect_system_call_definition = create_regular_system_call_definition(
    system_call_number=42,
)


sendto_system_call_definition = create_regular_system_call_definition(
    system_call_number=44,
)


recvfrom_system_call_definition = create_regular_system_call_definition(
    system_call_number=45,
    memory_address_registers=["rsi", 'r9']
)


sendmmsg_system_call_definition = create_regular_system_call_definition(
    system_call_number=46,
)


recvmsg_system_call_definition = create_regular_system_call_definition(
    system_call_number=47,
    memory_address_registers=['rsi']
)


bind_system_call_definition = create_regular_system_call_definition(
    system_call_number=49,
    # TODO
)


getsockname_system_call_definition = create_regular_system_call_definition(
    system_call_number=51,
    memory_address_registers=["rsi", "rdx"]
)


getpeername_system_call_definition = create_regular_system_call_definition(
    system_call_number=52,
    memory_address_registers=["rsi", "rdx"]
)


setsockopt_system_call_definition = create_regular_system_call_definition(
    system_call_number=54
)


getsockopt_system_call_definition = create_regular_system_call_definition(
    system_call_number=55,
    memory_address_registers=['r10']
)


uname_system_call_definition = create_regular_system_call_definition(
    system_call_number=63,
    memory_address_registers=["rdi"]
)


sendmmsg_system_call_definition = create_regular_system_call_definition(
    system_call_number=307,
    memory_address_registers=['rsi']
)


