import pytest
import subprocess
from pathlib import Path
import os


class CompileException(Exception):
    pass


def get_output_path_for_binary_with_name(name):
    return Path(f'/tmp/{name}.out')


@pytest.fixture
def compile_binary():
    binary_name = None

    def _compile_binary(directory, name, compile_args=None):
        nonlocal binary_name
        binary_name = name
        compile_args = compile_args or []
        success = os.system(f"gcc -o {get_output_path_for_binary_with_name(binary_name)} {directory}/{binary_name} {' '.join(compile_args)}")
        if success != 0:
            raise CompileException()
        os.system(f"chmod 777 {get_output_path_for_binary_with_name(binary_name)}")
    yield _compile_binary

    if binary_name:
        output_path = get_output_path_for_binary_with_name(binary_name)
        if output_path.exists():
            output_path.unlink()

    return _compile_binary


@pytest.fixture
def run_test_binary(compile_binary):
    process = None

    def _run_popen(directory, binary_name, compile_args=None, runtime_args=None):
        nonlocal process
        compile_args = compile_args or []
        runtime_args = runtime_args or []
        compile_binary(directory, binary_name, compile_args=compile_args)
        process = subprocess.Popen([str(get_output_path_for_binary_with_name(binary_name)), *runtime_args],
                                   stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process

    yield _run_popen
    if process is not None and process.poll() is None:
        process.terminate()
