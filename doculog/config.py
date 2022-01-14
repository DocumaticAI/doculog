"""
Parse user config
"""
import os
from configparser import ConfigParser, NoOptionError
from pathlib import Path
from typing import Dict

from dotenv import load_dotenv

from doculog.requests import validate_key


def set_env_vars(vars):
    for k, v in vars.items():
        os.environ[k] = v


def configure(project_root: Path) -> Dict:
    load_dotenv(project_root / ".env")
    config = parse_config(project_root)
    configure_api(config["local"])

    return config


def configure_api(local):
    if (not local) and (not validate_key()):
        if "DOCUMATIC_API_KEY" in os.environ:
            del os.environ["DOCUMATIC_API_KEY"]

        if "DOCULOG_API_KEY" in os.environ:
            del os.environ["DOCULOG_API_KEY"]


def parse_config(project_root: Path) -> Dict:
    print(f"Reading environment variables from {project_root / '.env.'}")
    load_dotenv(project_root / ".env")

    DEFAULT_VARS = {
        "DOCULOG_PROJECT_NAME": project_root.stem,
        "DOCULOG_RUN_LOCALLY": "false",
    }

    DEFAULT_CONFIG = {
        "changelog_name": "CHANGELOG.md",
        "local": False,
    }

    config_file = project_root / "pyproject.toml"

    if not config_file.exists():
        set_env_vars(DEFAULT_VARS)
        return DEFAULT_CONFIG

    config = ConfigParser()
    config.read(config_file)

    if not config.has_section("tool.doculog"):
        set_env_vars(DEFAULT_VARS)
        return DEFAULT_CONFIG

    # Environment variables
    try:
        project_name = config.get("tool.doculog", "project").strip("'").strip('"')
    except NoOptionError:
        project_name = DEFAULT_VARS["DOCULOG_PROJECT_NAME"]

    try:
        local = config.getboolean("tool.doculog", "local")
    except (NoOptionError, ValueError):
        local = False

    if "DOCUMATIC_API_KEY" not in os.environ and "DOCULOG_API_KEY" not in os.environ:
        print(
            "Environment variable DOCUMATIC_API_KEY not set. Advanced features disabled."
        )

    if "DOCULOG_API_KEY" in os.environ:
        print(
            "DOCULOG_API_KEY is deprecated and will be removed in v0.2.0. Use DOCUMATIC_API_KEY environment variable to set your api key instead."
        )

    os.environ["DOCULOG_PROJECT_NAME"] = project_name
    os.environ["DOCULOG_RUN_LOCALLY"] = str(local)

    # Config values
    try:
        changelog_name = config.get("tool.doculog", "changelog").strip("'").strip('"')
    except NoOptionError:
        changelog_name = DEFAULT_CONFIG["changelog_name"]

    if not changelog_name.endswith(".md"):
        changelog_name += ".md"

    return {"changelog_name": changelog_name, "local": local}
