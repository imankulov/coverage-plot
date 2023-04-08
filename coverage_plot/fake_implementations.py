import datetime
from typing import List

import faker
from attr import field, frozen

fake = faker.Faker()


@frozen
class FakeDeveloper:
    """
    Fake object implementing the subset of the interface of pydriller's Developer.

    Ref: https://pydriller.readthedocs.io/en/latest/commit.html
    """

    name: str = field(factory=fake.name)  # type: ignore
    email: str = field(factory=fake.email)  # type: ignore


@frozen
class FakeModification:
    """
    Fake object implementing the subset of the interface of pydriller's Modification.

    Ref: https://pydriller.readthedocs.io/en/latest/modifications.html
    """

    path: str = field(factory=fake.file_path)  # type: ignore

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

    author: FakeDeveloper = field(factory=FakeDeveloper)  # type: ignore
    author_date: datetime.datetime = field(
        factory=fake.date_time_this_year,  # type: ignore
    )
    msg: str = field(factory=fake.sentence)  # type: ignore
    hash: str = field(factory=fake.sha1)  # type: ignore
    modifications: List[FakeModification] = field(factory=list)  # type: ignore
