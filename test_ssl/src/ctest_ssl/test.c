#include <Python.h>
#include <stdio.h>
#include <openssl/rand.h>
#include <openssl/engine.h>

/**
 * Python module
 **/
PyObject *module = NULL;


static PyObject* run_random(PyObject *self, PyObject *args) {
  unsigned char bytes[500] = {0};
	if (RAND_bytes(bytes, 500) == 0) {
		printf("oh :(\n");
	}
	// OPENSSL_CTX_get0_public_drbg(NULL);
  // const RAND_METHOD *meth = RAND_get_rand_method();
	const ENGINE *engine = ENGINE_get_default_RAND();
	if (engine != NULL) {
		printf("%s", ENGINE_get_name(engine));printf("/n");
	} else {
		printf("FUCK\n");
	}
  return Py_BuildValue("y#", bytes, 500);
}

static PyMethodDef methods[]= {
	{"run_random", (PyCFunction)run_random, METH_NOARGS, "(todo docs)"},
	{NULL, NULL, 0, 0}
};


static struct PyModuleDef ctest_sslModule = {
	PyModuleDef_HEAD_INIT,
	"cpyrecorder",
	"description",
	-1,
	methods
};

PyMODINIT_FUNC PyInit_ctest_ssl(void) {
	module = PyModule_Create(&ctest_sslModule);
	return module;
}

