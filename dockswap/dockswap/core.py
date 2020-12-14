import os
import json
import subprocess
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from enum import Enum

from .errors import DockSwapError


class Composer(object):
    class Action(Enum):
        START = "up"
        STOP = "down"

    def __init__(
        self,
        docker_compose_path: Union[Path, str],
        env_path: Optional[Union[Path, str]] = None,
        binary_name: Optional[str] = None,
        project_name: Optional[str] = None,
    ):
        if isinstance(docker_compose_path, Path):
            docker_compose_path = docker_compose_path.absolute()
        if isinstance(env_path, Path):
            env_path = env_path.absolute()

        docker_compose_cli_env: str = os.environ.get(
            "DOCKSWAP_DOCKER_COMPOSE_CLI", "docker-compose"
        )

        self.docker_compose_path = str(docker_compose_path)
        self.env_path = str(env_path) if env_path else None
        self.binary_name = docker_compose_cli_env if not binary_name else binary_name
        self.project_name = project_name

    def start(self, dry: Optional[bool] = False, only: Optional[List[str]] = None):
        """
        Start containers for this composer.
        If `dry` is `True`, then just return command to be executed.
        `only` is list of names of containers to be started, for example
        if there are db, queue, backend services in composer file, user may
        want to start db and queue service only.
        """
        command = self.construct_command(Composer.Action.START, only)

        if dry:
            return command

        result = subprocess.run(command.split())
        if result.returncode != 0:
            self.fail(command, result.returncode)

    def stop(self, remove: Optional[bool] = False, dry: Optional[bool] = False):
        """
        Stop containers for this composer.
        If `dry` is `True`, then just return command to be executed.
        """
        command = self.construct_command(Composer.Action.STOP)

        if dry:
            return command

        result = subprocess.run(command.split())
        if result.returncode != 0:
            self.fail(command, result.returncode)

    def fail(self, command: str, returncode: int):
        raise DockSwapError(
            'Command "{}" exited with status code {}'.format(command, returncode)
        )

    def get_env_option(self):
        """Get --env-file option if self.env_path is specified"""
        return "--env-file {}".format(self.env_path) if self.env_path else ""

    def get_file_option(self):
        """Get -f option (path where .yml file is located)"""
        return "-f {}".format(self.docker_compose_path)

    def construct_command(
        self, action: Action, only: Optional[List[str]] = None
    ) -> str:
        """
        Contruct command to be executed depending of `action`.
        This function is to be used mainly as internal, but it is not private
        because interface allows for public usage for now.

        Also accept an `only` param (list of service names)
        that is to be used when starting specific
        containers defined in a service.
        """
        env_part = self.get_env_option() if action == Composer.Action.START else ""
        file_part = self.get_file_option()
        detached_part = "-d" if action == Composer.Action.START else ""
        only_part = " ".join(_only.strip() for _only in (only or []))
        command = "{dc_bin} {env_part} {file_part} {action} {detached_part} {only_part}".format(
            dc_bin=self.binary_name,
            env_part=env_part,
            file_part=file_part,
            action=action.value,
            detached_part=detached_part,
            only_part=only_part,
        ).strip()
        return " ".join(command.split())  # justify the command

    def __str__(self):
        return self.represent(full=True)

    def represent(self, full: bool = True):
        if full:
            return "{project_name} | docker-compose={docker_compose_path} env={env_path}".format(
                project_name=self.project_name,
                docker_compose_path=self.docker_compose_path,
                env_path=self.env_path or "X",
            )
        return self.project_name

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Composer":
        project_name = data.get("project_name", None)
        docker_compose_path = data.get("dc_path", None)
        env_path = data.get("env_path", None)

        if project_name and docker_compose_path:
            return cls(
                docker_compose_path=docker_compose_path,
                env_path=env_path,
                project_name=project_name,
            )

    def to_dict(self) -> Dict[str, str]:
        return {
            "project_name": self.project_name,
            "dc_path": self.docker_compose_path,
            "env_path": self.env_path,
        }


class DockSwapRepo(object):
    DOCKSWAP_DIR = ".dockswap"
    STORAGE_PATH = os.environ.get("DOCKSWAP_STORAGE_FILE_NAME", "storage.json")

    @classmethod
    def prune(cls):
        storage_path = Path.home() / Path(cls.DOCKSWAP_DIR) / Path(cls.STORAGE_PATH)
        storage_path.unlink()

    def __init__(self):
        self.dockswap_folder = Path.home() / Path(self.DOCKSWAP_DIR)
        self.dockswap_folder.mkdir(exist_ok=True)
        self.storage_path = self.dockswap_folder / Path(self.STORAGE_PATH)
        self.storage_path.touch()

        self._loaded_data: Optional[Dict[str, Any]] = None

    @property
    def loaded_data(self) -> List[Dict[str, str]]:
        """Lazy loaded raw composers data"""
        if not self._loaded_data:
            with open(self.storage_path, "r") as storage_file:
                try:
                    data = json.load(storage_file) or []
                except json.JSONDecodeError:
                    data = []

                self._loaded_data = data

            return self._loaded_data

        return self._loaded_data

    def commit(self, data: List[Dict[str, str]]):
        with open(self.storage_path, "w") as storage_file:
            json.dump(data, storage_file)

    def get_all(self) -> List[Composer]:
        composers = []
        for composer_data in self.loaded_data:
            built_composer = Composer.from_dict(composer_data)
            if built_composer:
                composers.append(built_composer)

        return composers

    def persist(self, composer: Composer):
        data = self.loaded_data + [composer.to_dict()]
        self.commit(data)

    def persist_all(self, composers: List[Composer], rewrite: bool = False):
        composers_data = [c.to_dict() for c in composers]

        if rewrite:
            self.commit(composers_data)
        else:
            self.commit(self.loaded_data + composers_data)

    def get(self, project_name: str, silent_not_found=False) -> Composer:
        composers = self.get_all()

        for composer in composers:
            if composer.project_name == project_name:
                return composer

        if silent_not_found:
            return None

        raise DockSwapError(
            'No composer found for "{}". May be register it first?'.format(project_name)
        )

    def delete(self, project_name: str) -> bool:
        composers = self.get_all()
        nice_composers = [c for c in composers if c.project_name != project_name]
        deleted = len(composers) != len(nice_composers)
        self.persist_all(nice_composers, rewrite=True)
        return deleted
