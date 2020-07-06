import pandas as pd

from coverage_plot.plot import (
    FileCoverage,
    export_df,
    import_json,
    import_xml,
    make_path_components,
    plot_sunburst,
)


def test_json_importer():
    json_report = """
    {
        "meta": {},
        "files": {
            "foo.py": {
                "executed_lines": [1, 2],
                "missing_lines": [3, 4, 5],
                "excluded_lines": [6, 7, 8, 9],
                "summary": {
                    "covered_lines": 2,
                    "num_statements": 9,
                    "percent_covered": 40.0,
                    "missing_lines": 3,
                    "excluded_lines": 4
                }
            }
        }
    }
    """.strip()
    report = import_json(json_report)
    assert "foo.py" in report
    assert report["foo.py"].percent_covered() == 40.0
    assert report["foo.py"].total_lines() == 5


def test_xml_importer():
    xml_report = """
    <?xml version="1.0" encoding="UTF-8"?>
    <coverage>
        <sources>
            <source>/app/foo</source>
        </sources>
        <packages>
            <package>
                <classes>
                    <class filename="app/views.py">
                        <methods/>
                        <lines>
                            <line hits="1" number="1"/>
                            <line hits="1" number="2"/>
                            <line hits="1" number="3"/>
                            <line hits="0" number="4"/>
                            <line hits="0" number="5"/>
                            <line hits="0" number="6"/>
                        </lines>
                    </class>
                </classes>
            </package>
        </packages>
    </coverage>
    """.strip()
    report = import_xml(xml_report)
    assert "foo/app/views.py" in report
    assert report["foo/app/views.py"].percent_covered() == 50.0
    assert report["foo/app/views.py"].total_lines() == 6


def test_make_path_components():
    df = pd.DataFrame([{"path": "foo/bar/baz.py"}])
    ret = make_path_components(df)
    assert dict(ret.iloc[0]) == {"p0": "foo", "p1": "bar", "p2": "baz.py"}


def test_export_df():
    report = {"app/foo.py": FileCoverage(1, 1), "app/bar.py": FileCoverage(2, 2)}
    df = export_df(report)
    assert list(df.columns) == [
        "path",
        "name",
        "total_lines",
        "percent_covered",
    ]


def test_sunburst():
    report = {
        "app/utils.py": FileCoverage(40, 3),
        "app/models/foo.py": FileCoverage(18, 1),
        "app/models/bar.py": FileCoverage(40, 20),
        "app/views/bar.py": FileCoverage(10, 20),
        "app/views/spam.py": FileCoverage(100, 90),
    }
    figure = plot_sunburst(report)
    assert figure.data[0].type == "sunburst"
