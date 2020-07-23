import glob
import os
from pathlib import Path
from setuptools import setup, find_packages, Extension

BASE_C_SOURCES_DIRECTORY = Path(__file__).resolve().parent / Path('cpager')
extension = Extension("cpager",
                      sources=[str(BASE_C_SOURCES_DIRECTORY / "cpager.c")],
                      extra_compile_args=['-Werror', '-L/usr/lib/x86_64-linux-gnu/'],
                      libraries=['protobuf-c', 'criu'],)

setup(name='pager',
      version='1.0',
      packages=find_packages(),
      ext_modules=[
          extension
      ],
      install_requires=['click', 'memory-tempfile', 'interruptingcow'],
      entry_points={
          'console_scripts': [
              'maor_pager = pager.cli:cli',
          ],
      }
      )
