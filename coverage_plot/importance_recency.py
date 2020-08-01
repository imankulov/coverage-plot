import os
from datetime import MINYEAR, datetime, timedelta
from typing import Dict, Iterator, List, cast

import attr

from coverage_plot.git_changes import (
    CommitFilter,
    ExcludeAllModifications,
    ExcludeAuthor,
    ExcludeMessage,
    IncludeAllCommits,
    IncludeFile,
    ModificationFilter,
    NormalizedModification,
    get_git_changes,
)
from coverage_plot.importance_interface import Importance


def year_ago():
    return datetime.utcnow() - timedelta(days=365)


@attr.s(auto_attribs=True)
class GitImportance(Importance):
    git_root: str
    commit_filters: List[CommitFilter] = attr.ib(
        factory=lambda: [
            ExcludeAuthor("bot"),
            ExcludeMessage("yapf"),
            ExcludeMessage("literals"),
            IncludeAllCommits(),
        ]
    )
    modification_filters: List[ModificationFilter] = attr.ib(
        factory=lambda: [IncludeFile("*.py"), ExcludeAllModifications()]
    )
    since: datetime = attr.ib(factory=year_ago)
    last_modified_dict: Dict[str, datetime] = attr.ib(
        factory=dict, init=False, repr=False
    )

    def __attrs_post_init__(self):
        git_changes = get_git_changes(
            self.git_root,
            self.commit_filters,
            self.modification_filters,
            since=self.since,
        )
        self.last_modified_dict = convert_to_last_modified(git_changes)

    def get_importance(self, filename: str) -> int:
        imp1 = self.get_recency_importance(filename)
        imp2 = self.get_filesize_importance(filename)
        return imp1 * imp2

    def get_recency_importance(self, filename: str) -> int:
        last_modified = self.last_modified_dict.get(filename)
        if last_modified is None:
            return 0
        return timestamp_to_importance(last_modified)

    def get_filesize_importance(self, filename: str) -> int:
        absolute_filename = os.path.join(self.git_root, filename)
        try:
            return os.stat(absolute_filename).st_size
        except FileNotFoundError:
            return 0


def timestamp_to_importance(last_modified: datetime) -> int:
    """
    Convert the timestamps to an importance metric.
    """
    base_importance = 1000
    now = datetime.utcnow()
    modified_weeks_ago = (now - last_modified).days // 7
    if modified_weeks_ago <= 0:
        return base_importance
    return base_importance // modified_weeks_ago


def convert_to_last_modified(
    modifications: Iterator[NormalizedModification],
) -> Dict[str, datetime]:
    """
    Take modifications and return the dict from filename to last modification timestamp.
    """
    sentinel = datetime(MINYEAR, 1, 1)
    last_modified_dict: Dict[str, datetime] = {}
    for mod in modifications:
        last_modified_dict[mod.path] = cast(
            datetime, max(mod.author_date, last_modified_dict.get(mod.path, sentinel)),
        )
    return last_modified_dict
