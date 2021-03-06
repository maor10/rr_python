import os
from pathlib import Path
from setuptools import setup, find_packages, Extension


BASE_C_INTERCEPTOR_DIRECTORY = Path('creplayer')

module = Extension("creplayer", sources=list(map(str, BASE_C_INTERCEPTOR_DIRECTORY.rglob("*.c"))),
                   extra_compile_args=['-Werror', '-D DEBUG=1'])

setup(name='replayer',
      version='1.0',
      packages=find_packages(),
      ext_modules=[module],
      install_requires=[],
      extras_require={
            'tests': ['pytest', 'interruptingcow', 'requests', 'flask', 'pymongo', 'mock']
      }
      )
