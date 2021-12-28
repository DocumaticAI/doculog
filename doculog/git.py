"""
Utility code for parsing git history.
"""
import re
import subprocess
from typing import Optional

leading_4_spaces = re.compile("^    ")


def get_commits(since_date: Optional[str] = None, until_date: Optional[str] = None):
    if since_date and until_date:
        command = ["git", "log", "--stat", "--since", since_date, "--until", until_date]
    else:
        command = ["git", "log", "--stat"]

    lines = (
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        .decode("utf-8")
        .split("\n")
    )

    commits = []
    current_commit = {}

    def save_current_commit():
        title = current_commit["message"][0]
        message = current_commit["message"][1:]
        changed_files = []

        if message and message[0] == "":
            del message[0]

        current_commit["title"] = title
        current_commit["message"] = "\n".join(message)
        current_commit["files"] = [
            _m.split("|")[0].strip() for _m in message if "|" in _m
        ]
        commits.append(current_commit)

    for line in lines:
        if not line.startswith(" "):
            if line.startswith("commit "):
                if current_commit:
                    save_current_commit()
                    current_commit = {}
                current_commit["hash"] = line.split("commit ")[1]
            else:
                try:
                    key, value = line.split(":", 1)
                    current_commit[key.lower()] = value.strip()
                except ValueError:
                    pass
        else:
            current_commit.setdefault("message", []).append(
                leading_4_spaces.sub("", line)
            )

    if current_commit:
        save_current_commit()

    commits.reverse()  # earliest commit first
    return commits


def _get_tag_date(tag_name: str) -> str:
    return (
        subprocess.check_output(
            ["git", "log", "-1", "--format=%ai", tag_name], stderr=subprocess.STDOUT
        )
        .decode("utf-8")
        .split(" ")[0]
    )


def list_tags():
    tags = (
        subprocess.check_output(["git", "tag", "-n"], stderr=subprocess.STDOUT)
        .decode("utf-8")
        .split("\n")
    )
    tags.reverse()

    tags = [t.split(" ")[0] for t in tags]
    tags = [(t, _get_tag_date(t)) for t in tags if t]
    return tags
