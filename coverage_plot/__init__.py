import pkg_resources

from coverage_plot.plot import import_json, import_xml, plot_sunburst, plot_treemap

__version__ = pkg_resources.get_distribution("coverage-plot").version
__all__ = ["import_json", "import_xml", "plot_sunburst", "plot_treemap", "__version__"]
