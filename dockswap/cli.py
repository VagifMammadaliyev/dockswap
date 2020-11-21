import os
import sys
import subprocess

from typing import Optional
from pathlib import Path
from enum import Enum

import typer
from dockswap.validators import (
    validate_docker_compose_path,
    validate_path,
    validate_project_name,
)
from dockswap.dockswap import Composer, DockSwapRepo
from dockswap.errors import DockSwapError

__author__ = "Vagif Mammadaliyev"
__email__ = "vagifmammadaliyev@outlook.com"
__version__ = "0.1.0"

VERSION = "0.1.1"
MAJOR, MINOR, PATCH = VERSION.split(".")

app = typer.Typer(help="DockSwap. Tool for swapping projects.")

docker_compose_path_help = (
    "Path to .yml or .json file that must be run using docker-compose"
)
env_path_help = (
    "If your docker-compose file uses env_file then specify path for that file"
)
dry_option = typer.Option(
    False, help="Do not run command, instead just print it"
)
remove_option = typer.Option(
    False, help="Stop and remove already running containers"
)

repo = DockSwapRepo()


class VersionPart(Enum):
    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"


@app.command()
def version(
    part: Optional[VersionPart] = typer.Option(
        None, help="which part of version to output"
    ),
    mini: Optional[bool] = typer.Option(
        False, help="output only version itself, useless if part is specified"
    ),
):
    """Shows version of currently used dockswap."""
    if not part:
        if mini:
            typer.echo(VERSION)
        else:
            typer.echo(
                "DockSwapping projects with v{version}".format(version=VERSION)
            )
    else:
        if part == VersionPart.MAJOR:
            typer.echo(MAJOR)
        elif part == VersionPart.MINOR:
            typer.echo(MINOR)
        elif part == VersionPart.PATCH:
            typer.echo(PATCH)


@app.command()
def add(
    project_name: str,
    path: Path = typer.Option(..., help=docker_compose_path_help),
    env_path: Optional[Path] = typer.Option(None, help=env_path_help),
):
    """Register composer for project"""
    validate_project_name(repo, project_name)
    if env_path:
        validate_path(env_path)
    validate_docker_compose_path(path)
    composer = Composer(
        docker_compose_path=path, env_path=env_path, project_name=project_name
    )
    repo.persist(composer)
    typer.secho(
        'Successfully registered composer for project "{}"'.format(
            project_name
        ),
        fg=typer.colors.GREEN,
    )


@app.command()
def list(full: Optional[bool] = typer.Option(False, help="show more info")):
    for i, composer in enumerate(repo.get_all(), start=1):
        typer.echo("{}. {}".format(i, composer.represent(full=full)))


@app.command()
def delete(project_name: str):
    deleted = repo.delete(project_name)
    if deleted:
        typer.secho(
            'Successfully removed "{}" from registered composers'.format(
                project_name
            ),
            fg=typer.colors.GREEN,
        )
    else:
        typer.secho(
            'Seems like composer for a project "{}" did not exist or already removed'.format(
                project_name
            ),
            fg=typer.colors.YELLOW,
        )


def stop_other_containers(
    remove: Optional[bool] = False, dry: Optional[bool] = False
):
    docker_bin = os.environ.get("DOCKSWAP_DOCKER_CLI", "docker")
    list_all_containers_command = "{} ps -aq".format(docker_bin)
    list_all_containers = subprocess.getoutput(list_all_containers_command)
    list_all_containers = " ".join(list_all_containers.split())

    stop_command_dry = "{} stop {}".format(docker_bin, list_all_containers)
    remove_command_dry = "{} rm {}".format(docker_bin, list_all_containers)

    if not list_all_containers:
        if dry:
            return None
        return

    if dry:
        commands = [stop_command_dry]

        if remove:
            commands.append(remove_command_dry)

        return " && ".join(commands)

    out = subprocess.run([docker_bin, "stop"] + list_all_containers.split())
    if out.returncode != 0:
        raise DockSwapError(
            'Command "{}" exited with status code {}'.format(
                stop_command_dry, out.returncode
            )
        )
    out = subprocess.run([docker_bin, "rm"] + list_all_containers.split())
    if out.returncode != 0:
        raise DockSwapError(
            'Command "{}" exited with status code {}'.format(
                remove_command_dry, out.returncode
            )
        )


@app.command()
def start(
    project_name: str,
    remove_other: Optional[bool] = remove_option,
    dry: Optional[bool] = dry_option,
):
    """Start containers for registered composer"""
    composer = repo.get(project_name)

    if remove_other and not dry:
        stop_other_containers(remove=True, dry=False)
    command = composer.start(dry=dry)

    if command and dry:
        if remove_other:
            remove_command = stop_other_containers(remove=True, dry=True)
            if not remove_command:
                return typer.echo(command)
            return typer.echo(" && ".join([remove_command, command]))
        typer.echo(command)

    if not dry:
        typer.secho("Successfully swapped a project!", fg=typer.colors.GREEN)


@app.command()
def stop(
    project_name: str,
    remove_other: Optional[bool] = remove_option,
    dry: Optional[bool] = dry_option,
):
    """Start containers for registered composer"""
    composer = repo.get(project_name)

    if remove_other and not dry:
        stop_other_containers(remove=True, dry=False)
    command = composer.stop(dry=dry)

    if command and dry:
        if remove_other:
            remove_command = stop_other_containers(remove=True, dry=True)
            if not remove_command:
                return typer.echo(command)
            return typer.echo(" && ".join([remove_command, command]))
        typer.echo(command)

    if not dry:
        typer.secho("Successfully stopped containers!", fg=typer.colors.GREEN)


@app.command()
def stopall(
    dry: Optional[bool] = dry_option, remove: Optional[bool] = remove_option
):
    command = stop_other_containers(remove=remove, dry=dry)
    if dry:
        typer.echo(command)
    else:
        typer.secho(
            "Successfully stopped{} all running containers!".format(
                " and removed" if remove else ""
            ),
            fg=typer.colors.GREEN,
        )


@app.command()
def prune(
    no_input: Optional[bool] = typer.Option(
        False, help="do not ask for confirmation"
    )
):
    def success():
        typer.secho("Pruned all registered composers", fg=typer.colors.GREEN)

    if no_input:
        DockSwapRepo.prune()
        success()
        return

    prune_yes = typer.confirm(
        "Are you sure to prune all your registered composers?"
    )

    if prune_yes:
        DockSwapRepo.prune()
        success()
    else:
        typer.secho("Pruning cancelled...", fg=typer.colors.YELLOW)


if __name__ == "__main__":
    try:
        app()
    except DockSwapError as dockswap_err:
        typer.secho(str(dockswap_err), fg=typer.colors.RED, err=True)
        sys.exit(1)
