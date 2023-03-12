import lifelines
import numpy
import plotly.graph_objs as go
import matplotlib.colors as mcolors


def _get_colors() -> list[tuple[float, float, float]]:
    colors_rgb = [mcolors.to_rgb(color) for color in mcolors.CSS4_COLORS.values()]
    dark_colors = list(
        filter(lambda x: sum(x) < 1.5, colors_rgb)
    )
    output_colors = []
    for i in range(len(dark_colors)):
        output_colors.append(dark_colors[i])
    return output_colors


colors = _get_colors()


def plot_kmf(
    plots: list[tuple[numpy.ndarray, numpy.ndarray, str]],
    limits: [tuple[float, float, float, float] | None] = None,
    show_conf: bool = False,
    show_median: bool = False,
) -> tuple[go.Figure, list[lifelines.KaplanMeierFitter]]:

    fig = go.Figure()

    kmf_results = []
    for plot, color in zip(plots, colors):
        r, g, b = color
        line_color = f"rgba({r}, {g}, {b})"
        conf_color = f"rgba({r}, {g}, {b}, 0.2)"

        durations, events, label = plot

        kmf = lifelines.KaplanMeierFitter()
        kmf.fit(durations, events, label=label)

        fig.add_trace(
            go.Scatter(
                name=label,
                x=kmf.survival_function_.index,
                y=kmf.survival_function_[label],
                mode="lines",
                line=dict(width=2, color=line_color),
                showlegend=True,
            )
        )
        if show_conf:
            fig.add_trace(
                go.Scatter(
                    x=kmf.confidence_interval_.index,
                    y=kmf.confidence_interval_[f'{label}_upper_0.95'],
                    mode="lines",
                    line=dict(shape='hv', width=0),
                    fill='tonexty',
                    fillcolor=conf_color,
                    showlegend=False
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=kmf.confidence_interval_.index,
                    y=kmf.confidence_interval_[f'{label}_lower_0.95'],
                    mode="lines",
                    line=dict(shape='hv', width=0),
                    fill='tonexty',
                    fillcolor=conf_color,
                    showlegend=False
                )
            )
        if show_median:
            fig.add_trace(
                go.Scatter(
                    name=label,
                    x=numpy.array([kmf.median_survival_time_ for _ in range(5)]),
                    y=numpy.linspace(0, 1, 5),
                    mode="lines",
                    line=dict(width=2, dash="dash", color=conf_color),
                    showlegend=False
                )
            )

    if limits:
        xmin, xmax, ymin, ymax = limits
        fig.update_xaxes(range=[xmin, xmax])
        fig.update_yaxes(range=[ymin, ymax])

    return fig, kmf_results


def subplots_kmf(
    fig: go.Figure(),
    row: int,
    col: int,
    durations: numpy.ndarray,
    events: numpy.ndarray,
    label: str,
    show_conf: bool = False,
    show_median: bool = False,
) -> None:

    kmf = lifelines.KaplanMeierFitter()
    kmf.fit(durations, events, label=label)

    fig.add_trace(
        go.Scatter(
            name=label,
            x=kmf.survival_function_.index,
            y=kmf.survival_function_[label],
            mode="lines",
            line=dict(width=2, color="rgba(255, 0, 0, 0.99)"),
            showlegend=False,
        ),
        row=row + 1,
        col=col + 1
    )
    if show_conf:
        fig.add_trace(
            go.Scatter(
                x=kmf.confidence_interval_.index,
                y=kmf.confidence_interval_[f'{label}_upper_0.95'],
                mode="lines",
                line=dict(shape='hv', width=0),
                fill='tonexty',
                fillcolor="rgba(255, 0, 0, 0.2)",
                showlegend=False
            ),
            row=row + 1,
            col=col + 1
        )
        fig.add_trace(
            go.Scatter(
                x=kmf.confidence_interval_.index,
                y=kmf.confidence_interval_[f'{label}_lower_0.95'],
                mode="lines",
                line=dict(shape='hv', width=0),
                fill='tonexty',
                fillcolor="rgba(255, 0, 0, 0.2)",
                showlegend=False
            ),
            row=row + 1,
            col=col + 1
        )
    if show_median:
        fig.add_trace(
            go.Scatter(
                x=numpy.array([kmf.median_survival_time_ for _ in range(5)]),
                y=numpy.linspace(0, 1, 5),
                mode="lines",
                line=dict(width=2, dash="dash", color="rgba(255, 0, 0, 0.2)"),
                showlegend=False
            ),
            row=row + 1,
            col=col + 1
        )
