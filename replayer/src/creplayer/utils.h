#ifndef UTILS_H
#define UTILS_H

#include <errno.h>
#include <Python.h>


#define RETURN_NULL_ON_TRUE(arg) if (arg) {   \
  return NULL; \
}


#define RAISE_EXCEPTION_ON_TRUE(arg, ...) if (arg) {   \
  PyErr_Format(PyExc_ValueError, __VA_ARGS__); \
  return NULL; \
}


#define RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(arg) if (arg) {   \
  PyErr_Format(PyExc_ValueError, "%s", strerror(errno)); \
  return NULL; \
}


#define RETURN_PY_NONE_ON_TRUE(arg) if (arg) {   \
  Py_RETURN_NONE;   \
}

#define LOG(...) printf(__VA_ARGS__);  \
  printf("\n");


#endif