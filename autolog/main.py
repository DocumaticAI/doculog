"""
CLI entrypoints to the code.
"""
from pathlib import Path

from autolog.changelog import ChangelogDoc
from autolog.config import configure


def generate_changelog():
    root = Path.cwd()

    config = configure(root)
    log_path = root / config["changelog_name"]

    doc = ChangelogDoc(log_path)
    doc.generate()
    doc.save()
    print(f"Saved changelog to {log_path}")
