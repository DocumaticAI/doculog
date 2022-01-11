"""
Unit tests for config.py
"""
import configparser
import os
from unittest import mock

import pytest

from doculog.config import configure_api, parse_config


class TestParseConfig:
    def test_can_parse_config(self, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
            [tool.doculog]
            changelog = CHANGELOG
            """
        )

        config = parse_config(tmp_path)
        assert config["changelog_name"] == "CHANGELOG.md"

    def test_can_parse_config_with_other_sections(self, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
            [tool.isort]
            profile = "black"

            [tool.doculog]
            changelog = CHANGELOG
            """
        )

        config = parse_config(tmp_path)
        assert config["changelog_name"] == "CHANGELOG.md"

    def test_can_parse_config_with_no_doculog_section(self, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
            [tool.isort]
            profile = "black"
            """
        )

        config = parse_config(tmp_path)
        assert config == {"changelog_name": "CHANGELOG.md", "local": False}

    def test_can_parse_config_if_pyproject_toml_does_not_exist(self, tmp_path):
        config = parse_config(tmp_path)
        assert config == {"changelog_name": "CHANGELOG.md", "local": False}

    def test_config_sets_project_name_environment_variable_if_set_in_config(
        self, tmp_path
    ):
        (tmp_path / "pyproject.toml").write_text(
            """
            [tool.doculog]
            project = "MyProject"
            """
        )

        parse_config(tmp_path)
        assert os.environ["DOCULOG_PROJECT_NAME"] == "MyProject"

    def test_config_sets_project_name_as_working_directory_if_not_provided_in_config(
        self,
        tmp_path,
    ):
        directory = tmp_path / "someproject"
        directory.mkdir()

        (directory / "pyproject.toml").write_text(
            """
            [tool.doculog]
            changelog = "changelog"
            """
        )

        parse_config(directory)
        assert os.environ["DOCULOG_PROJECT_NAME"] == "someproject"

    def test_parses_config_with_no_changelog_value(self, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
            [tool.doculog]
            some = value
            """
        )

        config = parse_config(tmp_path)
        assert config["changelog_name"] == "CHANGELOG.md"

    @pytest.mark.parametrize("changelog", ("CHANGELOG", "changelog", "release_notes"))
    def test_config_can_read_changelog_and_appends_md_filetype(
        self, tmp_path, changelog
    ):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            f"""
            [tool.doculog]
            changelog = {changelog}
            """
        )

        config = parse_config(tmp_path)
        assert config["changelog_name"] == changelog + ".md"

    @pytest.mark.parametrize(
        "changelog", ("CHANGELOG.md", "changelog.md", "release_notes.md")
    )
    def test_config_can_read_changelog_with_md_filetype(self, tmp_path, changelog):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            f"""
            [tool.doculog]
            changelog = {changelog}
            """
        )

        config = parse_config(tmp_path)
        assert config["changelog_name"] == changelog

    def test_local_is_false_if_not_provided_and_set_as_environment_variable(
        self, tmp_path
    ):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
            [tool.doculog]
            changelog = "changelog"
            """
        )

        config = parse_config(tmp_path)
        assert os.environ["DOCULOG_RUN_LOCALLY"] == "False"

    @pytest.mark.parametrize("local", ("True", "False"))
    def test_local_can_be_read_from_config_and_set_as_environment_var(
        self, tmp_path, local
    ):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            f"""
            [tool.doculog]
            local = {local.lower()}
            """
        )

        config = parse_config(tmp_path)
        assert os.environ["DOCULOG_RUN_LOCALLY"] == local

        # cleanup
        os.environ["DOCULOG_RUN_LOCALLY"] = "False"

    def test_local_is_set_to_false_if_in_config_as_non_bool_value(self, tmp_path):
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text(
            """
            [tool.doculog]
            local = "someothervalue"
            """
        )

        config = parse_config(tmp_path)
        assert os.environ["DOCULOG_RUN_LOCALLY"] == "False"

        # cleanup
        os.environ["DOCULOG_RUN_LOCALLY"] = "False"


class TestValidateAPI:
    @pytest.mark.parametrize("api_key", ("12345", "a2b3CDE199", "test"))
    @pytest.mark.parametrize("key_name", ("DOCULOG", "DOCUMATIC"))
    def test_sets_api_key_from_env_as_env_variable_if_valid_key_and_not_running_locally(
        self, api_key, mocker, key_name
    ):
        mocker.patch("doculog.config.validate_key", return_value=True)

        os.environ[f"{key_name}_API_KEY"] = api_key

        configure_api(False)
        assert os.environ[f"{key_name}_API_KEY"] == api_key
        del os.environ[f"{key_name}_API_KEY"]

    @pytest.mark.parametrize("api_key", ("12345", "a2b3CDE199", "test"))
    @pytest.mark.parametrize("key_name", ("DOCULOG", "DOCUMATIC"))
    def test_does_not_set_api_key_if_invalid_key_and_not_running_locally(
        self, api_key, mocker, key_name
    ):
        mocker.patch("doculog.config.validate_key", return_value=False)

        os.environ[f"{key_name}_API_KEY"] = api_key

        configure_api(False)
        assert os.getenv(f"{key_name}_API_KEY") is None

    @pytest.mark.parametrize("api_key", ("12345", "a2b3CDE199", "test"))
    @pytest.mark.parametrize("valid_key", (True, False))
    @pytest.mark.parametrize("key_name", ("DOCULOG", "DOCUMATIC"))
    def test_does_sets_api_key_if_present_and_running_locally(
        self, api_key, valid_key, mocker, key_name
    ):
        mocker.patch("doculog.config.validate_key", return_value=valid_key)

        os.environ[f"{key_name}_API_KEY"] = api_key

        configure_api(True)
        assert os.getenv(f"{key_name}_API_KEY") == api_key
        del os.environ[f"{key_name}_API_KEY"]

    @pytest.mark.parametrize("key_name", ("DOCULOG", "DOCUMATIC"))
    def test_does_not_error_when_validating_key_if_no_key_present(self, key_name):
        if f"{key_name}_API_KEY" in os.environ:
            del os.environ[f"{key_name}_API_KEY"]

        configure_api(False)
        assert os.getenv(f"{key_name}_API_KEY") is None
