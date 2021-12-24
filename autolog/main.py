"""
CLI entrypoints to the code.
"""
from pathlib import Path

from autolog.changelog import ChangelogDoc


def generate_changelog():
    log_path = Path.cwd() / "CHANGELOG.md"

    doc = ChangelogDoc(log_path)
    doc.generate()
    doc.save()
    print(f"Saved changelog to {log_path}")
