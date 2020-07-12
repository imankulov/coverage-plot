import datetime
import subprocess as subp
from typing import Optional

import attr

from coverage_plot.importance_interface import Importance


@attr.s(auto_attribs=True)
class GitImportance(Importance):
    git_root: str

    def get_importance(self, filename: str) -> int:
        last_modified = git_last_modified(filename, self.git_root)
        if last_modified is None:
            return 0
        return timestamp_to_importance(last_modified)


def timestamp_to_importance(last_modified: datetime.datetime) -> int:
    """
    Convert the timestamps to an importance metric.
    """
    base_importance = 1000
    now = datetime.datetime.utcnow()
    modified_weeks_ago = (now - last_modified).days // 7
    if modified_weeks_ago <= 0:
        return base_importance
    return base_importance // modified_weeks_ago


def git_last_modified(filename: str, git_root: str) -> Optional[datetime.datetime]:
    """
    For a given file in the git repository return the last modified timestamp.

    If the file is not found, return None.
    """
    raw_timestamp = subp.check_output(
        ["git", "log", "-1", "--format=%at", "--", filename], cwd=git_root,
    )
    timestamp_str = raw_timestamp.decode("utf8").strip()
    if not timestamp_str:
        return None  # file not found
    return datetime.datetime.fromtimestamp(int(timestamp_str))
