#ifndef UTILS_H
#define UTILS_H

#include <errno.h>
#include <Python.h>


#define RETURN_NULL_ON_TRUE(arg) if (arg) {   \
  LOG("Returning NULL (Raise last python error)");  \
  return NULL; \
}


#define RAISE_EXCEPTION_ON_TRUE(arg, ...) if (arg) {   \
  PyErr_Format(PyExc_ValueError, __VA_ARGS__); \
  LOG("Raising exception...");  \
  return NULL; \
}


#define RAISE_EXCEPTION_WITH_ERRNO_ON_TRUE(arg) if (arg) {   \
  PyErr_Format(PyExc_ValueError, "%s", strerror(errno)); \
  LOG("Raising exception with errno");  \
  return NULL; \
}


#define RETURN_PY_NONE_ON_TRUE(arg) if (arg) {   \
  Py_RETURN_NONE;   \
}

#define LOG(...) printf("%s:%i - ", __FILE__, __LINE__); \
    printf(__VA_ARGS__);  \
    printf("\n");

// #define LOG(...) ;

#endif