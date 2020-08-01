import datetime
from typing import List

import attr
import faker

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

fake = faker.Faker()


@attr.s(auto_attribs=True, frozen=True)
class FakeDeveloper:
    """
    Fake object implementing the subset of the interface of pydriller's Developer.

    Ref: https://pydriller.readthedocs.io/en/latest/commit.html
    """

    name: str = attr.ib(factory=fake.name)
    email: str = attr.ib(factory=fake.email)


@attr.s(auto_attribs=True, frozen=True)
class FakeModification:
    """
    Fake object implementing the subset of the interface of pydriller's Modification.

    Ref: https://pydriller.readthedocs.io/en/latest/modifications.html
    """

    path: str = attr.ib(factory=fake.file_path)

    @property
    def old_path(self):
        return self.path

    @property
    def new_path(self):
        return self.path


@attr.s(auto_attribs=True, frozen=True)
class FakeCommit:
    """
    Fake object implementing the subset of the interface of pydriller's Commit.
    """

    author: FakeDeveloper = attr.ib(factory=FakeDeveloper)
    author_date: datetime.datetime = attr.ib(factory=fake.date_time_this_year)
    msg: str = attr.ib(factory=fake.sentence)
    hash: str = attr.ib(factory=fake.sha1)
    modifications: List[FakeModification] = attr.ib(factory=list)


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
