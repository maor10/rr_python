import os
import sys
from pathlib import Path
import subprocess


try:
    import click
except ImportError:
    print("Please install click (pip install click) in order to continue installation")
    exit(0)


PACKAGES = ['replayer', 'pyrecorder', 'pager']


@click.group()
def cli():
    pass


@cli.command()
def install():
    directory = Path(__file__).parent.absolute()
    for package in PACKAGES:
        os.chdir(str((directory / package / 'src').absolute()))
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-e', '.[tests]'])


if __name__ == '__main__':
    cli()
