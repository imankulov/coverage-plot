import json
import os
from typing import Dict
from xml.etree import ElementTree as ET

import attr
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from coverage_plot.importance_interface import Importance

# Coverare Report, where str is a filename, and "FileCoverage"
# is the coverage result
Report = Dict[str, "FileCoverage"]


def import_json(content: str) -> Report:
    """Create a Report object from JSON-encoded content."""
    content_dict = json.loads(content)
    return import_dict(content_dict)


def import_dict(raw_report: Dict) -> Report:
    """Create a Report object from coverage.json."""
    report: Report = {}
    for filename, raw_coverage in raw_report["files"].items():
        coverage = FileCoverage.from_dict(raw_coverage)
        report[filename] = coverage
    return report


def import_xml(content: str) -> Report:
    report: Report = {}

    def is_covered(line_tag):
        return line_tag.attrib["hits"] != "0"

    tree = ET.fromstring(content)
    source = str(tree.findtext("sources/source"))
    if not source:
        source = ""
    root = os.path.basename(source)
    for tag in tree.iter("class"):
        filename = os.path.join(root, tag.attrib["filename"])
        line_tags = tag.findall("lines/line")
        covered_lines = sum([1 for line in line_tags if is_covered(line)], 0)
        missing_lines = sum([1 for line in line_tags if not is_covered(line)], 0)
        coverage = FileCoverage(
            covered_lines=covered_lines, missing_lines=missing_lines
        )
        report[filename] = coverage
    return report


def export_df(report: Report, importance: Importance) -> pd.DataFrame:
    """
    Covert Report and Importance objects to a pandas DataFrame.

    The DataFrame object has the following fields:

    - path (full path to the file)
    - name (the file name)
    - total_lines (total lines in the source file, as counted by coverage)
    - percent_covered (the percentage of the line)
    """
    records = []
    for filename, coverage in report.items():
        if filename == "":
            continue
        imp = importance.get_importance(filename)
        if imp == 0:
            continue
        record = {
            "path": filename,
            "name": os.path.basename(filename),
            "percent_covered": coverage.percent_covered(),
            "importance": imp,
        }
        records.append(record)

    records = sorted(records, key=lambda k: k["path"])
    return pd.DataFrame(records)


def make_path_components(report_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a dataframe with path components.
    """

    def splitter(path):
        chunks = {f"p{i}": component for i, component in enumerate(path.split("/"))}
        return pd.Series(chunks)

    return report_df["path"].apply(splitter)


@attr.s(frozen=True, auto_attribs=True)
class FileCoverage:
    covered_lines: int = 0
    missing_lines: int = 0

    def total_lines(self) -> int:
        return self.covered_lines + self.missing_lines

    @classmethod
    def from_dict(cls, raw_coverage: Dict):
        summary = raw_coverage["summary"]
        return FileCoverage(summary["covered_lines"], summary["missing_lines"])

    def percent_covered(self) -> float:
        """Return the percentage of the covered code."""
        covered_and_missing = self.covered_lines + self.missing_lines
        if covered_and_missing == 0:
            return 0.0
        return 100.0 * self.covered_lines / covered_and_missing


def plot_sunburst(report: Report, importance: Importance) -> Figure:
    """Return a sunburst Figure object from a report."""
    df = export_df(report, importance)
    path_components = make_path_components(df)
    summary = pd.concat([df, path_components], axis=1)
    return px.sunburst(
        summary,
        names="name",
        path=path_components.columns,
        values="importance",
        color="percent_covered",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
    )


def plot_treemap(report: Report, importance: Importance):
    """Return a treemap Figure object from a report."""
    df = export_df(report, importance)
    path_components = make_path_components(df)
    summary = pd.concat([df, path_components], axis=1)
    return px.treemap(
        summary,
        names="name",
        path=path_components.columns,
        values="importance",
        color="percent_covered",
        color_continuous_scale="RdYlGn",
        range_color=[0, 100],
    )
