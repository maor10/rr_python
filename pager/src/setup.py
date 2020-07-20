import glob
import os
from pathlib import Path
from setuptools import setup, find_packages, Extension

BASE_C_SOURCES_DIRECTORY = Path(__file__).resolve().parent / Path('cpager')
extension = Extension("cpager",
                      sources=[str(BASE_C_SOURCES_DIRECTORY / "cpager.c")],
                      # include_dirs=[str(BASE_C_SOURCES_DIRECTORY / Path('libs'))],
                      # extra_objects=[str(BASE_C_SOURCES_DIRECTORY / "libs" / "libcriu.a")],
                      libraries=['protobuf-c'])

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
