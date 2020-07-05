import click

from coverage_plot import import_json, plot_sunburst, plot_treemap


@click.command()
@click.option(
    "--plot-type",
    default="sunburst",
    type=click.Choice(["sunburst", "treemap"]),
    help="Set the plot type",
)
@click.option("--show/--no-show", default=True, help="Show the plot in a browser")
@click.option(
    "--save",
    type=click.Path(file_okay=True, dir_okay=False, writable=True, allow_dash=False),
    default=None,
    help="Save the plot in the HTML file",
)
@click.argument("coverage_file", type=click.File(mode="rt"))
def coverage_plot(plot_type, show, save, coverage_file):
    """
    Display a summary coverage plot from the coverage.json file.
    """
    plotters = {"sunburst": plot_sunburst, "treemap": plot_treemap}
    report = import_json(coverage_file.read())
    fig = plotters[plot_type](report)
    if show:
        fig.show()
    if save:
        fig.write_html(save)
