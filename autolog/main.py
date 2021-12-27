"""
CLI entrypoints to the code.
"""
from pathlib import Path

from autolog.changelog import ChangelogDoc
from autolog.config import parse_config


def generate_changelog():
    root = Path.cwd()

    config = parse_config(root)
    log_path = root / config["changelog_name"]

    doc = ChangelogDoc(log_path)
    doc.generate()
    doc.save()
    print(f"Saved changelog to {log_path}")
