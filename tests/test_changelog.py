import pytest

from doculog.changelog import ChangelogDoc, ChangelogRelease, ChangelogSection


class TestChangelogSection:
    def test_accepts_hyphen_bulleted_commit(self):
        section = ChangelogSection("Added")
        section.add_commit("- some new update")
        assert section._commits == ["- some new update"]

    def test_accepts_star_bulleted_commit(self):
        section = ChangelogSection("Added")
        section.add_commit("* some new update")
        assert section._commits == ["* some new update"]

    def test_accepts_hyphen_subbulleted_commit(self):
        section = ChangelogSection("Added")
        section.add_commit("  - some new update")
        assert section._commits == ["  - some new update"]

    def test_accepts_star_subbulleted_commit(self):
        section = ChangelogSection("Added")
        section.add_commit("  * some new update")
        assert section._commits == ["  * some new update"]

    def test_removing_duplicates_retains_order(self):
        # TODO: ideally repeat this N times
        commits = [
            "* a new commit",
            "* another new commit",
            "* some commit 3",
            "* some commit 4",
        ]

        section = ChangelogSection("Changed")
        section._commits = commits
        section.remove_duplicates()

        assert section._commits == commits

    def test_remove_duplicates(self):
        # TODO: ideally repeat this N times
        section = ChangelogSection("Changed")
        section._commits = [
            "* a new commit",
            "* another new commit",
            "* a new commit",
            "* some commit 3",
            "* some commit 4",
            "* some commit 3",
        ]
        section.remove_duplicates()

        expected_commits = [
            "* a new commit",
            "* another new commit",
            "* some commit 3",
            "* some commit 4",
        ]

        assert section._commits == expected_commits


class TestChangelogRelease:
    def test_generate_gets_commits_up_to_release_date(self, mocker):
        get_commits_mock = mocker.patch(
            "doculog.changelog.get_commits", return_value=[]
        )

        release = ChangelogRelease("0.1.0", "2021-12-25")
        release.generate("2021-12-01")
        get_commits_mock.assert_called_once_with(
            since_date="2021-12-01", until_date="2021-12-25"
        )

    @pytest.mark.parametrize(
        "keyword,change_type",
        (
            ("Make", "Added"),
            ("Add", "Added"),
            ("Tweaked", "Changed"),
            ("Remove", "Removed"),
            ("Fix", "Fixed"),
            ("Deprecate", "Deprecated"),
        ),
    )
    def test_catalog_commit_searches_first_word_for_keyword(self, keyword, change_type):
        commit = f"{keyword} a test commit"
        actual_type, _ = ChangelogRelease.catalog_commit(commit)

        assert actual_type == change_type

    @pytest.mark.parametrize(
        "keyword,change_type",
        (
            ("make", "Added"),
            ("add", "Added"),
            ("tweaked", "Changed"),
            ("remove", "Removed"),
            ("fix", "Fixed"),
            ("deprecate", "Deprecated"),
        ),
    )
    def test_catalog_commit_searches_lowercase_first_word_for_keyword(
        self, keyword, change_type
    ):
        commit = f"{keyword} a test commit"
        actual_type, _ = ChangelogRelease.catalog_commit(commit)

        assert actual_type == change_type

    @pytest.mark.parametrize(
        "firstword", ("Google", "Gazumped", "Tweet", "Did", "finally")
    )
    def test_catalog_commit_returns_None_type_but_unaltered_commit_if_first_word_not_keyword(
        self, firstword
    ):
        commit = f"{firstword} a test commit"
        actual_type, actual_update = ChangelogRelease.catalog_commit(commit)

        assert actual_type is None
        assert actual_update == commit

    @pytest.mark.parametrize(
        "update_type", ("Added", "Changed", "Fixed", "Deprecated", "Removed")
    )
    def test_read_populates_existing_section(self, update_type):
        existing_updates = [
            f"### {update_type}\n",
            "",
            "* an update",
            "  * a sub update",
            "* another update message",
            "- a third update",
            "### Some other section",
            "* this update should not be included",
        ]

        release = ChangelogRelease("test", "2021-12-25")
        release.read(existing_updates)

        for _section_type, _section in release._sections.items():
            if _section_type == update_type:
                assert _section._commits == [
                    "* an update",
                    "  * a sub update",
                    "* another update message",
                    "- a third update",
                ]
            else:
                assert _section._commits == []

    def test_read_populates_multiple_sections(self):
        existing_updates = [
            f"### Added\n",
            "",
            "* an update",
            "  * a sub update",
            "### Removed",
            "* something",
        ]

        release = ChangelogRelease("test", "2021-12-25")
        release.read(existing_updates)

        assert release._sections["Added"]._commits == [
            "* an update",
            "  * a sub update",
        ]
        assert release._sections["Removed"]._commits == ["* something"]

    def test_reads_empty_section(self):
        existing_updates = [f"### Added\n", "### Removed"]

        release = ChangelogRelease("test", "2021-12-25")
        release.read(existing_updates)

        for _section in release._sections.values():
            assert _section._commits == []


class TestChangelogDoc:
    def test_saves_if_git_enabled(self, tmp_path, mocker):
        mocker.patch("doculog.changelog.has_git", return_value=True)
        mocker.patch("doculog.changelog.list_tags", return_value=[])

        doc_path = tmp_path / "changelog.md"
        doc = ChangelogDoc(doc_path)
        doc.save()

        assert doc_path.exists()

    def test_does_not_save_if_git_not_enabled(self, tmp_path, mocker):
        mocker.patch("doculog.changelog.has_git", return_value=False)
        mocker.patch("doculog.changelog.list_tags", return_value=[])

        doc_path = tmp_path / "changelog.md"
        doc = ChangelogDoc(doc_path)
        doc.save()

        assert not doc_path.exists()
