import attr

from coverage_plot.importance_interface import Importance
from coverage_plot.plot import Report


@attr.s(auto_attribs=True)
class FileSizeImportance(Importance):
    """Get file importance based on the file size, as taken from the coverage report."""

    coverage_report: Report

    def get_importance(self, filename: str) -> int:
        file_coverage = self.coverage_report[filename]
        if not file_coverage:
            return 0
        return file_coverage.total_lines()
