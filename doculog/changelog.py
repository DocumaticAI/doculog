"""
Changelog framework.
"""
import re
from pathlib import Path
from typing import Optional, Tuple

from doculog.git import get_commits, has_git, list_tags
from doculog.requests import post


class ChangelogSection:
    """
    A section (e.g. Added, Removed, Changed) of a release.

    Attributes
    ----------
    title : str
        The title of the section
    _commits : list of str
        Each element is a "* " prepended changelog point

    Parameters
    ----------
    title : str
        The title of the section
    """

    def __init__(self, title: str) -> None:
        self.title = title
        self._commits = []

    def add_commit(self, commit_title: str):
        if not re.match(r"\s*[\*-]\s", commit_title):
            commit_title = "* " + commit_title

        self._commits.append(commit_title.rstrip())

    def has_content(self) -> bool:
        return len(self._commits) > 0

    def remove_duplicates(self) -> None:
        unique_commits = []
        for commit in self._commits:
            if commit not in unique_commits:
                unique_commits.append(commit)

        self._commits = unique_commits

    def __str__(self) -> str:
        content = f"### {self.title}\n\n"

        for _commit in self._commits:
            content += _commit + "\n"

        return content


class ChangelogRelease:
    """
    Changelog features related to a single release (git tag).

    Attributes
    ----------
    _version : str
        Tag of the version
    _date : str
        Date of version release. YYYY-MM-DD format.

    Parameters
    ----------
    version : str
    date : str
    """

    def __init__(self, version: str, date: str) -> None:
        self._version = version
        self._date = date

        self._sections = {
            "Added": ChangelogSection("Added"),
            "Changed": ChangelogSection("Changed"),
            "Fixed": ChangelogSection("Fixed"),
            "Removed": ChangelogSection("Removed"),
            "Deprecated": ChangelogSection("Deprecated"),
        }

        self._batched_commits = []

    def read(self, lines) -> None:
        for i, line in enumerate(lines):
            _line = line.lstrip("#").strip()

            if _line.lower() in ("added", "changed", "fixed", "removed", "deprecated"):
                title = _line.capitalize()

                for commit_line in lines[i + 1 :]:
                    if re.match(r"\s*[\*-]\s", commit_line):
                        self._sections[title].add_commit(commit_line)
                    elif re.match(r"#+\s", commit_line):
                        break

    def generate(self, start_date: str) -> None:
        commits = get_commits(since_date=start_date, until_date=self._date)

        for com in commits:
            if title := com["title"]:
                commit_type, clean_commit = self.catalog_commit(title)
                self.track_commit(commit_type, clean_commit)

        self.post_classification()

        for section in self._sections.keys():
            self._sections[section].remove_duplicates()

    def track_commit(self, commit_type: Optional[str], commit_update: str) -> None:
        """
        Track unclassified commits as a batch, then validate on a server.

        To limit idle-time for the end-user, commits are processed in batch.

        Parameters
        ----------
        commit_type : str or None
            Type of Changelog update. None if no type determined locally
        commit_update : str
            Commit message to be classfied into a Changelog section
        """
        self._batched_commits.append((commit_type, commit_update))

        if len(self._batched_commits) >= 25:
            self.post_classification()

    def post_classification(self) -> None:
        """
        Classify commit updates on a server.

        The server contains additional and ML-driven logic for determining
        whether a commit is a valid Changelog update.
        If classified commits are returned, they are added to the correct section
        in the Changelog.
        """
        if len(self._batched_commits) > 0:
            if classified_commits := post(
                "classify", self._batched_commits, params={"version": self._version}
            ):
                self._update_log(classified_commits)
            else:
                self._update_log(self._batched_commits)

            self._batched_commits = []

    def _update_log(self, log_updates) -> None:
        for commit_type, commit_msg in log_updates:
            if commit_type:
                self._sections[commit_type].add_commit(commit_msg)

    @staticmethod
    def catalog_commit(commit: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Naively catalog a commit based on the leading word.

        Expects commits to be started by an imperitive verb,
        however non-imperitive will also be considered.

        Returns
        -------
        str or None
            The type of the commit.
        str or None
            The "cleaned" commit. Leading keyword removed.
        """
        commit_types = {
            "fixed": "Fixed",
            "fixes": "Fixed",
            "fix": "Fixed",
            "bugfix": "Fixed",
            "solve": "Fixed",
            "solves": "Fixed",
            "solved": "Fixed",
            "close": "Fixed",
            "closes": "Fixed",
            "closed": "Fixed",
            "corrects": "Fixed",
            "correct": "Fixed",
            "corrected": "Fixed",
            "create": "Added",
            "creates": "Added",
            "created": "Added",
            "make": "Added",
            "makes": "Added",
            "made": "Added",
            "write": "Added",
            "wrote": "Added",
            "add": "Added",
            "adds": "Added",
            "added": "Added",
            "list": "Changed",
            "lists": "Changed",
            "use": "Changed",
            "uses": "Changed",
            "fetch": "Changed",
            "fetches": "Changed",
            "fetched": "Changed",
            "log": "Changed",
            "logs": "Changed",
            "logged": "Changed",
            "improve": "Changed",
            "improves": "Changed",
            "improved": "Changed",
            "print": "Changed",
            "prints": "Changed",
            "printed": "Changed",
            "rewrite": "Changed",
            "rewrote": "Changed",
            "rewrit": "Changed",
            "refactor": "Changed",
            "change": "Changed",
            "changes": "Changed",
            "changed": "Changed",
            "move": "Changed",
            "moves": "Changed",
            "moved": "Changed",
            "update": "Changed",
            "updates": "Changed",
            "updated": "Changed",
            "tweak": "Changed",
            "tweaks": "Changed",
            "tweaked": "Changed",
            "remove": "Removed",
            "removes": "Removed",
            "removed": "Removed",
            "delete": "Removed",
            "deletes": "Removed",
            "deleted": "Removed",
            "deprecate": "Deprecated",
            "deprecates": "Deprecated",
            "deprecated": "Deprecated",
        }

        commit_lower = commit.lower()
        cleaned_commit = None
        start_word = commit_lower.split(" ")[0]

        try:
            commit_type = commit_types[start_word]
            cleaned_commit = commit_lower.replace(start_word, "").strip().capitalize()
            return commit_type, cleaned_commit
        except KeyError:
            return None, commit

    def header(self) -> str:
        return f"## {self._version} - {self._date}"

    def __str__(self) -> str:
        content = self.header() + "\n\n"

        for section in self._sections.values():
            if section.has_content():
                content += str(section).strip() + "\n\n"

        return content


class ChangelogUnreleased(ChangelogRelease):
    """
    Unreleased feature set.

    Unlike a tagged release,
    "Unreleased" does not show a date in its changelog header.
    """

    def __init__(self) -> None:
        # Use some far future date to get all unreleased commits
        # Some dates, e.g. 2100-12-31, yield 0 commits.
        # TODO: Need to work out why
        super().__init__("Unreleased", "2099-01-01")

    def header(self) -> str:
        return f"## {self._version}"


class ChangelogDoc:
    """
    The Changelog, comprised of 1 or many releases.

    Attributes
    ----------
    _releases : dict [str: ChangelogRelease]
        Keys are release tags
    _changelog_path : pathlib.Path
        Path to changelog file
    _tags : list of (str, str)
        List of git tags.
        First element of tuple is git tag name.
        Second element of tuple is git tag date.
    """

    def __init__(self, changelog_path: Path) -> None:
        self._releases = {}
        self._changelog_path = changelog_path
        self._tags = list_tags()

        self.has_git = has_git()

    def _get_tag_date(self, tag_name: str) -> str:
        for tag, tag_date in self._tags:
            if tag == tag_name:
                return tag_date

    def read(self) -> None:
        if not self._changelog_path.exists():
            return

        with open(self._changelog_path, "r") as f:
            content = f.readlines()

        curr_version = None
        version_date = None
        curr_lines = []

        def _read_release():
            if curr_version is not None:
                if curr_version.lower() == "unreleased":
                    new_release = ChangelogUnreleased()
                else:
                    new_release = ChangelogRelease(curr_version, version_date)

                new_release.read(curr_lines)
                self._releases[curr_version] = new_release

        for line in content:
            _line = line.lstrip("#").strip()
            _line_parts = _line.split("-")
            _ver = _line_parts[0].strip().lstrip("v")

            if (
                re.match(r"[0-9]{1,2}\.[0-9]{1,2}\.[0-9]{1,2}", _ver)
                or _ver.lower() == "unreleased"
            ):
                _read_release()

                curr_version = _ver
                curr_lines = []
                if len(_line_parts) == 2:
                    version_date = _line_parts[1].strip()
                else:
                    version_date = str(self._get_tag_date("v" + _ver))

            else:
                curr_lines.append(line)

        _read_release()

    def generate(self) -> None:
        if not self.has_git:
            print(
                "Git not enabled in current working directory. Not generating Changelog."
            )
            return

        self.read()

        if "Unreleased" not in self._releases or (
            len(self._tags) > 0 and self._tags[0][0].lstrip("v") not in self._releases
        ):
            # Either no unreleased or existing unreleased has become new tagged version
            self._releases["Unreleased"] = ChangelogUnreleased()

        if len(self._tags) > 0:
            unreleased_start_date = self._tags[0][1]
        else:
            unreleased_start_date = "1999-01-01"

        self._releases["Unreleased"].generate(unreleased_start_date)

        for i, (tag_name, tag_date) in enumerate(self._tags):
            vless_tag = tag_name.lstrip("v").strip()

            if vless_tag in self._releases:
                continue

            if i == len(self._tags) - 1:
                section_start = "1999-01-01"
            else:
                section_start = self._tags[i + 1][1]

            release = ChangelogRelease(vless_tag, tag_date)
            release.generate(section_start)
            self._releases[vless_tag] = release

    def __str__(self) -> str:
        content = (
            "# Changelog\n\nBased on KeepAChangelog.\nGenerated by **Documatic.**\n\n"
        )

        if "Unreleased" in self._releases:
            content += str(self._releases["Unreleased"]).strip()

        for tag_name, _ in self._tags:
            vless_tag_name = tag_name.lstrip("v").strip()

            if vless_tag_name in self._releases:
                content += "\n\n" + str(self._releases[vless_tag_name]).strip()

        content += "\n"  # newline at end of file

        return content

    def save(self) -> None:
        if self.has_git:
            with open(self._changelog_path, "w") as f:
                f.write(str(self))
