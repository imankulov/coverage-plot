# Coverage Plot

[![codecov](https://codecov.io/gh/imankulov/coverage-plot/branch/master/graph/badge.svg)](https://codecov.io/gh/imankulov/coverage-plot)
[![Coverage Status](https://coveralls.io/repos/github/imankulov/coverage-plot/badge.svg)](https://coveralls.io/github/imankulov/coverage-plot)
[![Maintainability](https://api.codeclimate.com/v1/badges/0f758ae06864812dce12/maintainability)](https://codeclimate.com/github/imankulov/coverage-plot/maintainability)
[![Documentation Status](https://readthedocs.org/projects/coverage-plot/badge/?version=latest)](https://coverage-plot.readthedocs.io/en/latest/?badge=latest)

A library and a script to plot Python code coverage results.

## Getting Started

Run the tests for your project with the test coverage, and convert the coverage results to a JSON or XML format. As a result, you should find a coverage.json or coverage.xml file in your current working directory.

```
coverage run pytest
coverage xml  # or coverage json
```

Install the package.

```
pip install coverage-plot
```

Run the coverage visualization. The script opens the browser with the visualization results.

```
coverage-plot coverage.xml
```
