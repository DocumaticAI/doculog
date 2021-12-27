"""
Unit tests for config.py
"""
import configparser
import os

import pytest

from autolog.config import parse_config


def test_can_parse_config(tmp_path):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        """
        [tool.autolog]
        changelog = CHANGELOG
        """
    )

    config = parse_config(tmp_path)
    assert config == {"changelog_name": "CHANGELOG.md"}


def test_can_parse_config_with_other_sections(tmp_path):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        """
        [tool.isort]
        profile = "black"

        [tool.autolog]
        changelog = CHANGELOG
        """
    )

    config = parse_config(tmp_path)
    assert config == {"changelog_name": "CHANGELOG.md"}


def test_can_parse_config_with_no_autolog_section(tmp_path):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        """
        [tool.isort]
        profile = "black"
        """
    )

    config = parse_config(tmp_path)
    assert config == {"changelog_name": "CHANGELOG.md"}


def test_can_parse_config_if_pyproject_toml_does_not_exist(tmp_path):
    config = parse_config(tmp_path)
    assert config == {"changelog_name": "CHANGELOG.md"}


def test_config_sets_project_name_environment_variable_if_set_in_config(tmp_path):
    (tmp_path / "pyproject.toml").write_text(
        """
        [tool.autolog]
        project = MyProject
        """
    )

    parse_config(tmp_path)
    assert os.environ["AUTOLOG_PROJECT_NAME"] == "MyProject"


def test_config_sets_project_name_as_working_directory_if_not_provided_in_config(
    tmp_path,
):
    directory = tmp_path / "someproject"
    directory.mkdir()

    (directory / "pyproject.toml").write_text(
        """
        [tool.autolog]
        changelog = changelog
        """
    )

    parse_config(directory)
    assert os.environ["AUTOLOG_PROJECT_NAME"] == "someproject"


def test_parses_config_with_no_changelog_value(tmp_path):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        """
        [tool.autolog]
        some = value
        """
    )

    config = parse_config(tmp_path)
    assert config == {"changelog_name": "CHANGELOG.md"}


@pytest.mark.parametrize("changelog", ("CHANGELOG", "changelog", "release_notes"))
def test_config_can_read_changelog_and_appends_md_filetype(tmp_path, changelog):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        f"""
        [tool.autolog]
        changelog = {changelog}
        """
    )

    config = parse_config(tmp_path)
    assert config == {"changelog_name": changelog + ".md"}


@pytest.mark.parametrize(
    "changelog", ("CHANGELOG.md", "changelog.md", "release_notes.md")
)
def test_config_can_read_changelog_with_md_filetype(tmp_path, changelog):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        f"""
        [tool.autolog]
        changelog = {changelog}
        """
    )

    config = parse_config(tmp_path)
    assert config == {"changelog_name": changelog}


@pytest.mark.parametrize("api_key", ("12345", "a2b3CDE199", "test"))
def test_sets_api_key_from_env_as_env_variable(tmp_path, api_key):
    (tmp_path / "pyproject.toml").touch()
    (tmp_path / ".env").write_text(
        f"""
        AUTOLOG_API_KEY = {api_key}
        """
    )

    parse_config(tmp_path)
    assert os.environ["AUTOLOG_API_KEY"] == api_key
    del os.environ["AUTOLOG_API_KEY"]


def test_local_is_false_if_not_provided_and_set_as_environment_variable(tmp_path):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        """
        [tool.autolog]
        changelog = changelog
        """
    )

    config = parse_config(tmp_path)
    assert os.environ["AUTOLOG_RUN_LOCALLY"] == "False"


@pytest.mark.parametrize("local", ("True", "False"))
def test_local_can_be_read_from_config_and_set_as_environment_var(tmp_path, local):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        f"""
        [tool.autolog]
        local = {local.lower()}
        """
    )

    config = parse_config(tmp_path)
    assert os.environ["AUTOLOG_RUN_LOCALLY"] == local

    # cleanup
    os.environ["AUTOLOG_RUN_LOCALLY"] = "False"


def test_local_is_set_to_false_if_in_config_as_non_bool_value(tmp_path):
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(
        """
        [tool.autolog]
        local = someothervalue
        """
    )

    config = parse_config(tmp_path)
    assert os.environ["AUTOLOG_RUN_LOCALLY"] == "False"

    # cleanup
    os.environ["AUTOLOG_RUN_LOCALLY"] = "False"
