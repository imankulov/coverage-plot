# Coverage Plot

A library and a script to plot Python code coverage results.

## Getting Started

Run the tests for your project with the test coverage, and convert the coverage results to a JSON or XML format. As a result, you shoud find a coverage.json or coverage.xml file in your current working directory.

```
coverage run pytest
coverage xml  # or coverage json
```

Install the package.

```
pip install coverage-plot
```

Run the coverage visualization. The script opens the browser with the visualization-results.

```
coverage-plot coverage.xml
```
