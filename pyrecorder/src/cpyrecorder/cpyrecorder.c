#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <frameobject.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/ptrace.h>
#include <linux/ptrace.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>

#include "utils.h"


#define STOP_STEP 0
#define STOP_NEXT 1
#define STOP_RET 2


/**
 * Python module
 **/
PyObject *module = NULL;


/**
 * At which frame should we stop?
 * TODO: Understand where this will be set
 **/
PyFrameObject *stop_frame;


/**
 * Stop type
 **/
int stop_type;


int fork_and_debug() {
  return 0;
}


int should_stop(PyFrameObject *frame) {
  switch (stop_type)
  {
  case STOP_NEXT:
    return stop_frame == frame;
    break;
  case STOP_STEP:
    return frame->f_back == stop_frame; 
    break;
  case STOP_RET:
    return stop_frame->f_back == frame;
    break;
  default:
    break;
  }
  return 0;
}


// TODO: figure out what are these params
int tracer(PyObject *obj, PyFrameObject *frame, int what, PyObject *obj2) {
  if (what == PyTrace_LINE) {
    if (should_stop(frame)) {
      // TODO: make this run our debugger
      PyRun_SimpleString("import ipdb; ipdb.set_trace();");
    }
  }
  return 0;
}

static PyObject* record_or_replay(PyObject *self, PyObject *args) {
  PyThreadState *state;

  // check if replaying  
  // TODO: how to know??
  if (1) {
    state = PyGILState_GetThisThreadState();
    // We need to check if c_traceobj is NULL, as Python will XDECREF it in PyEval_SetTrace, 
    // potentially creating a difference in the memory between record and replay when the garbage collector comes 
    RAISE_EXCEPTION_ON_TRUE (state->c_traceobj != NULL, "Trace obj is currently set! Replaying will potentially corrupt memory state :/");
    PyEval_SetTrace(tracer, NULL);
    LOG("Set trace func\n");
  }

  Py_RETURN_NONE;
}


static PyMethodDef methods[]= {
	{"record_or_replay", (PyCFunction)record_or_replay, METH_VARARGS, "(todo docs)"},
	{NULL, NULL, 0, 0}
}; 


static struct PyModuleDef cpyrecorderModule = {
	PyModuleDef_HEAD_INIT,
	"cpyrecorder",
	"description",
	-1,
	methods
};

PyMODINIT_FUNC PyInit_cpyrecorder(void) {
	module = PyModule_Create(&cpyrecorderModule);
  PyModule_AddStringConstant(module, "version", "1.0.0");
	return module;
}

