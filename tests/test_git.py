import subprocess

from doculog.git import has_git


class TestHasGit:
    def test_returns_true_if_git_log_does_not_error(self, mocker):
        mocker.patch("doculog.git.subprocess.check_output", return_value=None)
        assert has_git()

    def test_returns_false_if_git_log_errors(self, mocker):
        mocker.patch(
            "doculog.git.subprocess.check_output",
            side_effect=subprocess.CalledProcessError("some error", "some error"),
        )
        assert not has_git()
