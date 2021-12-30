"""
CLI entrypoints to the code.
"""
from pathlib import Path

from doculog.changelog import ChangelogDoc
from doculog.config import configure


def generate_changelog():
    root = Path.cwd()

    config = configure(root)
    log_path = root / config["changelog_name"]

    doc = ChangelogDoc(log_path)
    doc.generate()
    doc.save()

    if log_path.exists():
        print(f"Saved changelog to {log_path}")
