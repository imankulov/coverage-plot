import abc
import enum
import fnmatch
from datetime import datetime, timezone
from typing import Generator, Iterator, List, Optional

from attrs import frozen
import pydriller
from pydriller import Commit, Modification


class FilterResult(enum.Enum):
    INCLUDE = "INCLUDE"
    EXCLUDE = "EXCLUDE"
    DONT_KNOW = "DONT_KNOW"


@frozen
class NormalizedModification:
    hash: str
    msg: str
    author_name: str
    author_email: str
    author_date: datetime
    path: str

    @classmethod
    def from_commit_modification(cls, commit: Commit, modification: Modification):
        return NormalizedModification(
            hash=commit.hash,
            msg=commit.msg,
            author_name=commit.author.name,
            author_email=commit.author.email,
            author_date=commit.author_date.astimezone(timezone.utc).replace(
                tzinfo=None
            ),
            path=modification.old_path or modification.new_path,
        )


class CommitFilter(abc.ABC):
    def filter_commit(self, commit: Commit) -> FilterResult:
        ...


class ModificationFilter(abc.ABC):
    def filter_modification(self, modification: Modification) -> FilterResult:
        ...


@frozen
class ExcludeAuthor(CommitFilter):
    author_name: str

    def filter_commit(self, commit: Commit) -> FilterResult:
        if self.author_name in commit.author.name:
            return FilterResult.EXCLUDE
        if self.author_name in commit.author.email:
            return FilterResult.EXCLUDE
        return FilterResult.DONT_KNOW


@frozen
class ExcludeMessage(CommitFilter):
    message: str

    def filter_commit(self, commit: Commit) -> FilterResult:
        if self.message in commit.msg:
            return FilterResult.EXCLUDE
        return FilterResult.DONT_KNOW


@frozen
class ExcludeAllCommits(CommitFilter):
    def filter_commit(self, commit: Commit) -> FilterResult:
        return FilterResult.EXCLUDE


@frozen
class IncludeAllCommits(CommitFilter):
    def filter_commit(self, commit: Commit) -> FilterResult:
        return FilterResult.INCLUDE


@frozen
class IncludeFile(ModificationFilter):

    file_pattern: str

    def filter_modification(self, modification: Modification) -> FilterResult:
        path = modification.old_path or modification.new_path
        if fnmatch.fnmatch(path, self.file_pattern):
            return FilterResult.INCLUDE
        return FilterResult.DONT_KNOW


@frozen
class ExcludeAllModifications(ModificationFilter):
    """
    Catch-all filter to exclude all modifications.

    Add to the end of the list to filters to define the default behavior as
    "exclude the modification."
    """

    def filter_modification(self, modification: Modification) -> FilterResult:
        return FilterResult.EXCLUDE


@frozen
class IncludeAllModifications(ModificationFilter):
    """
    Catch-all filter to incldue all modifications.

    Add to the end of the list to filters to define the default behavior as
    "include the modification."
    """

    def filter_modification(self, modification: Modification) -> FilterResult:
        return FilterResult.INCLUDE


def get_git_changes(
    git_root: str,
    commit_filters: List[CommitFilter],
    modification_filters: List[ModificationFilter],
    since: Optional[datetime] = None,
) -> Generator[NormalizedModification, None, None]:
    """
    Take a git repository and iterate over the list of modifications.

    The commit_filters and modification_filters parameters are required. If you want to
    accept all the commits, and all the modifications, pass
    [IncludeAllCommits()], [IncludeAllModifications()]
    """
    commits = pydriller.RepositoryMining(git_root, since=since).traverse_commits()
    return filter_modifications(commits, commit_filters, modification_filters)


def filter_modifications(
    commits: Iterator[Commit],
    commit_filters: List[CommitFilter],
    modification_filters: List[ModificationFilter],
) -> Generator[NormalizedModification, None, None]:
    for commit in commits:
        if apply_commit_filters(commit, commit_filters) == FilterResult.EXCLUDE:
            continue
        for mod in commit.modifications:
            filter_result = apply_modification_filters(mod, modification_filters)
            if filter_result == FilterResult.EXCLUDE:
                continue
            yield NormalizedModification.from_commit_modification(commit, mod)


def apply_commit_filters(commit: Commit, commit_filters: List[CommitFilter]):
    for filt in commit_filters:
        result = filt.filter_commit(commit)
        if result in (FilterResult.INCLUDE, FilterResult.EXCLUDE):
            return result
    raise RuntimeError(f"Don't know what to do with commit {commit}")


def apply_modification_filters(
    modification: Modification, modification_filters: List[ModificationFilter]
):
    for filt in modification_filters:
        result = filt.filter_modification(modification)
        if result in (FilterResult.INCLUDE, FilterResult.EXCLUDE):
            return result
    raise RuntimeError(f"Don't know what to do with modification {modification}")
