obj-m += record.o
record-objs := main.o syscall_recorder.o syscall_wrapper.o copy_to_user_wrapper.o utils.o syscall_dumper.o recorded_processes_loader.o

ccflags-y += -I $(PWD)/include/

all:
	make -C $(BUILD_DIR) M=$(CURDIR) modules

clean:
	make -C $(BUILD_DIR) M=$(CURDIR) clean