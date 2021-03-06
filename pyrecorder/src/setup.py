from pathlib import Path

from setuptools import setup, find_packages, Extension

BASE_C_INTERCEPTOR_DIRECTORY = Path('cpyrecorder')


module = Extension("cpyrecorder", sources=list(map(str, BASE_C_INTERCEPTOR_DIRECTORY.rglob("*.c"))),
                   include_dirs=["/home/osboxes/openssl/include/"],
                   extra_compile_args=['-Werror'],
                   libraries=['crypto'])


setup(name='pyrecorder',
      version='1.0',
      packages=find_packages(),
      install_requires=[],
      extras_require={
          'tests': ['pytest', 'ipdb', 'psutil', 'interruptingcow', 'dataset', 'mysqlclient'],
      },
      ext_modules=[module],
      )
