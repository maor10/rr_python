#include <criu/criu.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <Python.h>
#include "utils.h"


#define LOG_FILE "log.txt"

PyObject *module = NULL;


/**
 * Setup criu for both dumping and restoring
 **/
PyObject* setup_criu(const char *file_path) {
  int dir_fd = open(file_path, O_DIRECTORY);
  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(dir_fd == -1);

  // the following functions cannot fail (each returns void), they are merely setup
  criu_init_opts();
  criu_set_tcp_established(1);
  criu_set_log_file(LOG_FILE);
  criu_set_shell_job(1);
  criu_set_work_dir_fd(dir_fd);
  criu_set_images_dir_fd(dir_fd);

  return Py_BuildValue("");
}


static PyObject* take_snapshot(PyObject* self, PyObject *args) {
  pid_t pid = 0;
  const char* file_path = NULL;

  if (!PyArg_ParseTuple(args, "is", &pid, &file_path))  {
    return NULL;
  }

  RETURN_NULL_ON_TRUE(setup_criu(file_path) == NULL);
  // following funcs cannot fail, merely setup
  criu_set_pid(pid);
  criu_set_leave_running(1);

  RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(criu_dump() < 0);

  return Py_BuildValue("");
}


static PyObject* restore_from_snapshot(PyObject* self, PyObject* args) {
  int res = 0;
  char* file_path = NULL;

  if (!PyArg_ParseTuple(args, "s", &file_path))  {
      return NULL;
  }
  RETURN_NULL_ON_TRUE(setup_criu(file_path) == NULL);
  
  res = criu_restore();
  // TODO: is errno not set? check if you can do this in a slightly more.. normal fashion 
  if (res < 0) {
      PyErr_Format(PyExc_ValueError, "%s", strerror(res * -1));
      return NULL;
  }

  return Py_BuildValue("");
}


static PyMethodDef methods[]= {
  {"take_snapshot", (PyCFunction)take_snapshot, METH_VARARGS, "take snapshot"},
  {"restore_from_snapshot", (PyCFunction)restore_from_snapshot, METH_VARARGS, "restore from snapshot"},
  {NULL, NULL, 0, 0}
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
