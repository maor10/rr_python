import json
import os

import click
import cpager
from pager import Listener
from pager.consts import BASE_DIRECTORY, DUMP_DIRECTORY


def is_root_user() -> bool:
    return os.geteuid() == 0


@click.group()
def cli():
    pass


@cli.command()
def start_listener():
    if not is_root_user():
        print("You must be root to run the listener")
        return
    BASE_DIRECTORY.mkdir(parents=True, exist_ok=True)
    Listener.create().run()


@cli.command()
def list_pids():
    print(json.dumps(os.listdir(BASE_DIRECTORY), indent=4))


@cli.command()
# @click.option('--pid', prompt='PID to restore')
def restore():
    if not is_root_user():
        print("You must be root to run restore")
        return
    cpager.restore_from_snapshot(str(DUMP_DIRECTORY))


if __name__ == '__main__':
    cli()
