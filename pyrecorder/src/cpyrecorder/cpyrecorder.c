#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include <frameobject.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/user.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <signal.h>


#include "utils.h"


#define STOP_STEP 0
#define STOP_NEXT 1
#define STOP_RET 2

#define FAILED_OPENING_PDB -1
#define IN_PARENT 0
#define IN_PDB 1


#define REPLAY_ENVIRONMENT_FILE_PATH "/tmp/replay"
#define REPLAY_STOP_TYPE_FILE_PATH "/tmp/replay_"


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
int stop_type = -1;


/**
 * Returns 1/-1 on forked process, and 0 on parent 
 **/
int fork_and_debug() {
  if (fork() == 0) {
   // TODO what to run here???
   return PyRun_SimpleString("import ipdb; ipdb.set_trace();") == 0; 
  } else {
    // Wait to be woken up to continue
    kill(getpid(), SIGSTOP);
    
  }
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
      return fork_and_debug();
    }
  }
  return 0;
}


int in_replay_environment() {
  FILE *file = fopen(REPLAY_ENVIRONMENT_FILE_PATH, "r");
  if (file){
    fclose(file);
    return 1;
  }
  return 0;
}


void handler(int signum) //, siginfo_t *info, void *extra)
{
  LOG("GOT HERE!!!!");
    // void *ptr_val = info->si_value.sival_ptr;
    // int int_val = info->si_value.sival_int;
    // printf("Child: Father, I am %d!\n",int_val);
}


int get_and_set_stop_type() {
//  char file_name = REPLAY_ENVIRONMENT_FILE_PATH;
//  FILE *file = fopen(REPLAY_ENVIRONMENT_FILE_PATH, "r");
return -1;
}

static PyObject* record_or_replay(PyObject *self, PyObject *args) {
  PyThreadState *state;
  // check if replaying  
  // TODO: how to know??
  if (in_replay_environment()) {
    state = PyGILState_GetThisThreadState();
    // We need to check if c_traceobj is NULL, as Python will XDECREF it in PyEval_SetTrace, 
    // potentially creating a difference in the memory between record and replay when the garbage collector comes 
    RAISE_EXCEPTION_ON_TRUE (state->c_traceobj != NULL, "Trace obj is currently set! Replaying will potentially corrupt memory state :/");
    PyEval_SetTrace(tracer, NULL);
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
  PyModule_AddStringConstant(module, "REPLAY_ENVIRONMENT_FILE_PATH", REPLAY_ENVIRONMENT_FILE_PATH);
	return module;
}

