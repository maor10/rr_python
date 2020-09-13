obj-m += record.o

record-objs += main.o
record-objs += utils.o
record-objs += record_manager/record_manager.o
record-objs += record_manager/recording_control_procfile.o
record-objs += events_manager/events_manager.o
record-objs += events_manager/events_dump_procfile.o
record-objs += rdtsc_record/rdtsc_recorder.o
record-objs += syscall_record/syscall_recorder.o
record-objs += copy_to_user_record/copy_to_user_recorder.o
record-objs += wrapped_copy_to_user_record/wrapped_copy_to_user_recorder.o

ccflags-y += -I $(PWD)/include/

all:
	make -C $(BUILD_DIR) M=$(CURDIR) modules

clean:
	make -C $(BUILD_DIR) M=$(CURDIR) clean