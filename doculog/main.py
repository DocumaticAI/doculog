"""
CLI entrypoints to the code.
"""
from pathlib import Path
from argparse import ArgumentParser

from doculog.config import configure
from doculog import ChangelogDoc, __version__


def generate_changelog():
    root = Path.cwd()

    config = configure(root)
    log_path = root / config["changelog_name"]

    doc = ChangelogDoc(log_path)
    doc.generate()
    doc.save()

    if log_path.exists():
        print(f"Saved changelog to {log_path}")


parser = ArgumentParser(
    prog=f"Doculog v{__version__}",
)

parser.add_argument("--cl", "-change-log", 
    action="store_true",
    dest="cl",
    help="Generates changelog for project"
)

def parse():
    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    if not args:
        # Some message or default text displayed here maybe
        # Command Used: doculog
        exit(0)

    if args["cl"]:
        # Called when --cl or -change-log flag is used
        generate_changelog()

    exit(0)
