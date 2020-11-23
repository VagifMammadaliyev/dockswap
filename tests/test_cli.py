#!/usr/bin/env python
import os
from typing import Union

import pytest
from faker import Faker
from typer.testing import CliRunner, Result

os.environ["DOCKSWAP_STORAGE_FILE_NAME"] = "_storage_test.json"

from dockswap import cli  # noqa: E402

app = cli.app
runner = CliRunner()
faker = Faker()


@pytest.fixture(scope="session", autouse=True)
def mock_stopper(session_mocker):
    real_stop = cli.Composer.stop

    def stop(*args, **kwargs):
        kwargs["dry"] = True
        return real_stop(*args, **kwargs)

    session_mocker.patch("dockswap.cli.Composer.stop", stop)


@pytest.fixture(scope="session", autouse=True)
def mock_starter(session_mocker):
    real_start = cli.Composer.start

    def start(*args, **kwargs):
        kwargs["dry"] = True
        return real_start(*args, **kwargs)

    session_mocker.patch("dockswap.cli.Composer.start", start)


def run_command(command: str, assert_exit_code=0):
    """
    Thin wrapper for runner.invoke(app, ...).
    If `assert_exit_code` is not None,
    then assert commands exit code.
    """
    command = command.split()
    result = runner.invoke(app, command)

    if assert_exit_code is not None:
        try:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        except ValueError:
            print("Not captured stdout or stderr")
        assert result.exit_code == assert_exit_code

    return result


def command_result(result: Union[str, Result]):
    """Append \\n to expected result."""
    if isinstance(result, Result):
        result = result.stdout
    return result.strip() + "\n"


_ = command_result


@pytest.fixture
def current_version():
    return cli.VERSION


@pytest.fixture
def mock_path_validators(mocker):
    mocker.patch("dockswap.cli.validate_path", return_value=None)
    mocker.patch(
        "dockswap.cli.validate_docker_compose_path",
        return_value=None,
    )


@pytest.fixture
def mock_empty_repo(mocker):
    mocker.patch("dockswap.cli.repo._loaded_data", [])


@pytest.fixture
def mock_full_repo(mocker, fake_storage):
    mocker.patch("dockswap.cli.repo._loaded_data", fake_storage(5))


@pytest.fixture
def fake_storage_data():
    def _fake_storage_data(name=None, file=None, env=None):
        return {
            "dc_path": file or faker.file_path(extension="yml"),
            "env_path": env or faker.file_path(),
            "project_name": name or faker.word(),
        }

    return _fake_storage_data


@pytest.fixture
def fake_storage(fake_storage_data):
    def _fake_storage(n=5):
        data = [fake_storage_data() for _ in range(n)]
        return data

    return _fake_storage


@pytest.fixture(autouse=True)
def mock_persist(mocker):
    def persist(*args, **kwargs):
        pass

    mocker.patch("dockswap.cli.repo.persist", persist)


@pytest.fixture
def concrete_storage(fake_storage_data):
    def _concrete_storage(names, files=None, envs=None):
        none_list = [None] * len(names)
        files = files or none_list
        envs = envs or none_list
        data = [
            fake_storage_data(name=name, file=fn, env=env)
            for name, fn, env in zip(names, files, envs)
        ]
        return data

    return _concrete_storage


def test_version(current_version):
    result = run_command("version")
    assert current_version in result.stdout


def test_version_mini(current_version):
    result = run_command("version --mini")
    assert result.stdout == _(current_version)


def test_version_parts(current_version):
    major, minor, patch = current_version.split(".")
    parts = ["major", "minor", "patch"]
    errors = {}
    for expected, part in zip([major, minor, patch], parts):
        result = run_command("version --part {}".format(part))
        if not result.stdout == _(expected):
            errors[part] = {"expected": expected, "current": result.stdout}

    error_message = "; ".join(
        "Expected {}, got {} for part={}".format(
            error["expected"], error["current"], part
        )
        for part, error in errors.items()
    )
    assert not errors, error_message


def test_list_composers_with_no_composers(mock_empty_repo):
    result = run_command("list")
    assert result.stdout == "", "No composer is actually saved!"


def test_add_composer(mock_path_validators, mocker, mock_empty_repo):
    result = run_command(
        "add project --path /path/to/file.yml --env-path /path/env"
    )
    assert "success" in result.stdout.lower()


def test_list_composer_with_existing_composers(mock_full_repo, mocker):
    result = run_command("list")
    assert len(result.stdout.splitlines()) == 5


def test_add_composer_with_used_name(mocker, fake_storage_data):
    mocker.patch(
        "dockswap.cli.repo._loaded_data", [fake_storage_data(name="foo")]
    )
    result = run_command(
        "add foo --path /path/to/file.yml --env-path /path/env", 1
    )
    assert "already registered" in result.stdout


def test_delete_composer(mocker, fake_storage_data):
    mocker.patch(
        "dockswap.cli.repo._loaded_data", [fake_storage_data(name="foo")]
    )
    result = run_command("delete foo")
    assert "success" in result.stdout.lower()


def test_start_composer(mocker, concrete_storage):
    mocker.patch(
        "dockswap.cli.repo._loaded_data", concrete_storage(names=["foo"])
    )
    result = run_command("start foo")
    assert "swap" in result.stdout.lower()


def test_stop_composer(mocker, concrete_storage):
    mocker.patch(
        "dockswap.cli.repo._loaded_data", concrete_storage(names=["foo"])
    )
    result = run_command("stop foo")
    assert "stopped" in result.stdout.lower()


def test_start_composer_dry(mocker, concrete_storage):
    mocker.patch(
        "dockswap.cli.repo._loaded_data",
        concrete_storage(names=["foo"], files=["foo.yml"], envs=["env"]),
    )
    result = run_command("start foo --dry")
    assert result.stdout == _("docker-compose --env-file env -f foo.yml up -d")


def test_start_unexisting_composer(mocker, concrete_storage):
    mocker.patch(
        "dockswap.cli.repo._loaded_data",
        concrete_storage(names=["foo"]),
    )
    result = run_command("start bar", 1)
    assert "no composer" in result.stdout.lower()
