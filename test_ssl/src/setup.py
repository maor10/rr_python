from pathlib import Path

from setuptools import setup, find_packages, Extension

BASE_C_INTERCEPTOR_DIRECTORY = Path('ctest_ssl')


module = Extension("ctest_ssl", sources=list(map(str, BASE_C_INTERCEPTOR_DIRECTORY.rglob("*.c"))),
                   extra_compile_args=['-Werror'],
                   libraries=['crypto'])


setup(name='test_ssl',
      version='1.0',
      packages=find_packages(),
      install_requires=[],
      ext_modules=[module],
      )
