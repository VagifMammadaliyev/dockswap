from pathlib import Path

from .errors import DockSwapError


def validate_path(path: Path):
    """
    Check if path exists at all.
    """
    if not path.exists() or path.is_dir():
        raise DockSwapError(
            f"{path} is not a valid file path. May be you have provided a directory?"
        )


def validate_docker_compose_path(path: Path):
    """
    Check if file's extension is .yml or .json. Although this is a very
    naive approach, as the file could be YAML of JSON, but not a valid docker composer.
    """
    validate_path(path)

    # TODO: Add better validation here
    if path.suffix.lstrip(".") not in ["yml", "json"]:
        raise DockSwapError(
            '"{path}" is not a valid YAML/JSON path'.format(path=path)
        )


def validate_project_name(repo, name: str):
    """
    Check if project with `name` is alread registered.
    """
    if repo.get(name, silent_not_found=True):
        raise DockSwapError(
            'Composer for project "{name}" is already registered.'
            " Consider removing it first".format(name=name)
        )
