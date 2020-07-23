#include <criu/criu.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <Python.h>


#define RAISE_PYTHON_ERROR_ON_FAIL(arg) if (arg < 0) { PyErr_Format(PyExc_ValueError, "%s (%d)", strerror(errno), arg); return NULL; }
#define LOG_FILE "log.txt"

PyObject *module = NULL;


static PyObject* take_snapshot(PyObject* self, PyObject *args) {
    int pid = 0;
    int dir_fd = 0;
    const char* file_path = NULL;

    if (!PyArg_ParseTuple(args, "is", &pid, &file_path))  {
        return NULL;
    }

    dir_fd = open(file_path, O_DIRECTORY);

    criu_init_opts();
    criu_set_pid(pid);
    criu_set_tcp_established(true);
    criu_set_log_file(LOG_FILE);
    criu_set_shell_job(true);
    criu_set_leave_running(true);
    criu_set_work_dir_fd(dir_fd);
    criu_set_images_dir_fd(dir_fd);
    RAISE_PYTHON_ERROR_ON_FAIL(criu_dump());

    return Py_BuildValue("");
 }


static PyObject* restore_from_snapshot(PyObject* self, PyObject* args) {
    int dir_fd = 0;
    int res = 0;
    char* file_path = NULL;

    if (!PyArg_ParseTuple(args, "s", &file_path))  {
        return NULL;
    }

    dir_fd = open(file_path, O_DIRECTORY);

    criu_init_opts();
    criu_set_shell_job(true);
    criu_set_tcp_established(true);
    criu_set_log_file(LOG_FILE);
    criu_set_images_dir_fd(dir_fd);
    criu_set_work_dir_fd(dir_fd);
    res = criu_restore();
    if (res < 0) {
        PyErr_Format(PyExc_ValueError, "%s", strerror(res * -1));
        return NULL;
    }

    return Py_BuildValue("");
}


 static PyMethodDef methods[]= {
     {"take_snapshot", (PyCFunction)take_snapshot, METH_VARARGS, "take snapshot"},
     {"restore_from_snapshot", (PyCFunction)restore_from_snapshot, METH_VARARGS, "restore from snapshot"},
     {NULL, NULL, NULL, 0, NULL}
 };


 static struct PyModuleDef cpagerModule = {
     PyModuleDef_HEAD_INIT,
     "cpager",
     "description",
     -1,
     methods
 };


 PyMODINIT_FUNC PyInit_cpager(void) {
     module = PyModule_Create(&cpagerModule);
     PyModule_AddStringConstant(module, "version", "0.0.1");
     return module;
 }
