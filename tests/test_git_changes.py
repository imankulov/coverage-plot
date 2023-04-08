import faker

from coverage_plot.fake_implementations import (
    FakeCommit,
    FakeDeveloper,
    FakeModification,
)
from coverage_plot.git_changes import (
    ExcludeAllModifications,
    ExcludeAuthor,
    ExcludeMessage,
    FilterResult,
    IncludeAllCommits,
    IncludeFile,
    apply_commit_filters,
    apply_modification_filters,
    filter_modifications,
)


def test_include_file_include():
    m1 = FakeModification(path="foo.py")
    assert IncludeFile("*.py").filter_modification(m1) == FilterResult.INCLUDE


def test_include_file_dont_know():
    m2 = FakeModification(path="foo.txt")
    assert IncludeFile("*.py").filter_modification(m2) == FilterResult.DONT_KNOW


def test_exclude_message_exclude():
    commit = FakeCommit(msg="Apply black formatting")
    assert ExcludeMessage("black").filter_commit(commit) == FilterResult.EXCLUDE


def test_exclude_message_dont_know():
    commit = FakeCommit(msg="Refactor something")
    assert ExcludeMessage("black").filter_commit(commit) == FilterResult.DONT_KNOW


def test_exclude_author_exclude():
    commit = FakeCommit(author=FakeDeveloper(name="robot"))
    assert ExcludeAuthor("robot").filter_commit(commit) == FilterResult.EXCLUDE


def test_exclude_author_dont_know():
    commit = FakeCommit(author=FakeDeveloper(name="roman"))
    assert ExcludeAuthor("robot").filter_commit(commit) == FilterResult.DONT_KNOW


commits = [
    # Filter out by commit message (black)
    FakeCommit(
        author=FakeDeveloper(name="roman"),
        msg="Apply black formatting",
        modifications=[FakeModification(path="foo.py")],
    ),
    # Filter out one of two files by the name (not a Python)
    FakeCommit(
        author=FakeDeveloper(name="roman"),
        msg="Add README",
        modifications=[
            FakeModification(path="README.md"),
            FakeModification(path="readme.py"),
        ],
    ),
]


def test_apply_commit_filters():
    commit = FakeCommit(
        author=FakeDeveloper(name="roman"),
        msg="Apply black formatting",
        modifications=[FakeModification(path="foo.py")],
    )
    commit_filters = [ExcludeMessage("black"), IncludeAllCommits()]
    assert apply_commit_filters(commit, commit_filters) == FilterResult.EXCLUDE


def test_apply_modification_filters():
    modification = FakeModification(path="README.md")
    modification_filters = [IncludeFile("*.py"), ExcludeAllModifications()]
    assert (
        apply_modification_filters(modification, modification_filters)
        == FilterResult.EXCLUDE
    )


def test_filter_commits():
    commit_filters = [ExcludeMessage("black"), IncludeAllCommits()]
    modification_filters = [IncludeFile("*.py"), ExcludeAllModifications()]

    modifications = list(
        filter_modifications(commits, commit_filters, modification_filters)
    )
    assert len(modifications) == 1
    assert modifications[0].msg == "Add README"
    assert modifications[0].path == "readme.py"
