"""
CLI entrypoints to the code.
"""
from pathlib import Path
from argparse import ArgumentParser
import os
import logging

from doculog.config import configure
from doculog import ChangelogDoc, __version__

logger = logging.getLogger(__name__)


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
    prog="doculog",
    description=f"Doculog v{__version__}",
)

parser.add_argument("-cl", "--changelog", 
    action="store_true",
    dest="cl",
    help="generates changelog for project"
)

parser.add_argument("-ow", "--overwrite",
    action="store_true",
    dest="ow",
    help="overwrites current CHANGELOG if present"
)

def parse():
    args = {k: v for k, v in vars(parser.parse_args()).items() if v is not None}

    if (not args) or args["cl"]:
        # Builds changelog if cl flag is present or no args provided
        logger.debug("Generating changelog")
        generate_changelog()

    if args["ow"]:
        if os.path.exists("./CHANGELOG.md"):
            os.remove("./CHANGELOG.md")
            logger.info("Deleted original changelog, generating from scratch")
        else:
            logger.warn("Overwrite flag provided, but not file found")

    exit(0)
