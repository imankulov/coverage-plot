import datetime
from typing import List

from attr import field, frozen


@frozen
class FakeDeveloper:
    """
    Fake object implementing the subset of the interface of pydriller's Developer.

    Ref: https://pydriller.readthedocs.io/en/latest/commit.html
    """

    name: str = field(default="John Doe")
    email: str = field(default="john.doe@example.com")


@frozen
class FakeModification:
    """
    Fake object implementing the subset of the interface of pydriller's Modification.

    Ref: https://pydriller.readthedocs.io/en/latest/modifications.html
    """

    path: str = field(default="src/models.py")

    @property
    def old_path(self):
        return self.path

    @property
    def new_path(self):
        return self.path


@frozen
class FakeCommit:
    """
    Fake object implementing the subset of the interface of pydriller's Commit.
    """

    author: FakeDeveloper = field(factory=FakeDeveloper)
    author_date: datetime.datetime = field(default=datetime.datetime(2023, 1, 1))
    msg: str = field(default="Add a new feature")
    hash: str = field(default="1234567890abcdef1234567890abcdef12345678")
    modifications: List[FakeModification] = field(factory=list)
