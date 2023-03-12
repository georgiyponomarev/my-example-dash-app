from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, dash_table
from lifelines.datasets import load_leukemia

from functions import plot_kmf, subplots_kmf


data = load_leukemia()

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.ZEPHYR],
    assets_folder="./assets"
)

app.layout = html.Div([
    html.Link(
        id="theme-link",
        rel="stylesheet",
        href="./assets/light.css"
    ),
    dbc.Container([
        # title
        dbc.Row([
            dbc.Col(
                dbc.Button(
                    "dark mode",
                    id='theme-selector',
                    className='mb-3 button',
                    n_clicks=0
                ),
                width=2
            ),
            dbc.Col(
                html.H1("Comparing different leukemia treatments"),
                className="mb-2 header"
            )
        ]),

        # show and describe the data
        dbc.Card([
            html.H4("Explore the data"),
            html.P(
                "Move the slider to show a selected number of rows",
                className="subtitle",
            ),
            dcc.Slider(
                id="slider",
                min=1,
                max=len(data),
                step=1,
                value=7,
                marks={i: str(i) for i in range(1, len(data) + 1, 3)}
            ),
            dash_table.DataTable(
                id="data-table",
                columns=[{"name": i, "id": i} for i in data.columns],
                data=data.to_dict('records'),
                page_size=7,
            )],
            id="table-1",
            className="card mb-4 text-center",
        ),

        dbc.Row([
            dbc.Col([
                # Kaplan-Meier survival estimate for the whole dataset
                dbc.Card([
                    html.H4("Kaplan-Meier survival estimate"),
                    dcc.Graph(id="km-estimate-overall"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Checklist(
                                id="show-conf-checkbox-overall",
                                options=["show confidence intervals"],
                                value=[]
                            )
                        ]),
                        dbc.Col([
                            dcc.Checklist(
                                id="show-overall-median-time",
                                options=["show median survival time"],
                                value=[]
                            )
                        ])
                    ])],
                    id="plot-1",
                    className="card mb-4 text-center",
                ),
            ], xs=12, sm=12, md=12, lg=12, xl=6),
            dbc.Col([
                # Kaplan-Meier survival estimates for different treatments
                dbc.Card([
                    html.H4("Survival times for different treatments"),
                    dcc.Graph(id="km-estimate-treatments"),
                    dbc.Row([
                        dbc.Col([
                            dcc.Checklist(
                                id="show-conf-checkbox-treatments",
                                options=["show confidence intervals"],
                                value=[]
                            )
                        ]),
                        dbc.Col([
                            dcc.Checklist(
                                id="show-medians",
                                options=["show median survival times"],
                                value=[]
                            )
                        ])
                    ])],
                    id="plot-2",
                    className="card mb-4 text-center",
                )
            ], xs=12, sm=12, md=12, lg=12, xl=6)
        ]),

        # survival times by sex and by treatment
        dbc.Card([
            html.H4("Survival times by sex and by treatment method"),
            dcc.Dropdown(
                options=[
                    'Male, treatment 0',
                    'Female, treatment 0',
                    'Male, treatment 1',
                    'Female, treatment 1',
                ],
                value=['Male, treatment 0'],
                multi=True,
                id='survival-dropdown'
            ),
            dcc.Graph(id="survival-subplots"),
            dbc.Row([
                dbc.Col([
                    dcc.Checklist(
                        id="show-conf-subplots",
                        options=["show confidence intervals"],
                        value=[]
                    )
                ]),
                dbc.Col([
                    dcc.Checklist(
                        id="show-medians-subplots",
                        options=["show median survival time"],
                        value=[]
                    )
                ])
            ])
        ],
            id="subplots",
            className="card mb-4 text-center",
        ),
        dbc.Card(
            html.H4(
                html.A(
                    children="source",
                    href=(
                        "https://github.com/chrisluedtke/data-science-journal/blob/master/"
                        "07-Advanced-Regression/02_Survival_Analysis.ipynb"
                    ),
                    target="_blank",
                ),
                className="text-center text-light",
            ),
            className="mb-4"
        )
    ])
],
    id="application"
)


@app.callback(
    [
        Output(component_id="theme-link", component_property="href"),
        Output(component_id="theme-selector", component_property="children")
    ],
    Input(component_id="theme-selector", component_property="n_clicks")
)
def update_theme(n_clicks):
    if n_clicks % 2 == 0:
        return './assets/light.css', 'dark theme'
    else:
        return './assets/dark.css', 'light theme'


@app.callback(
    Output(component_id="data-table", component_property="page_size"),
    Input(component_id="slider", component_property="value")
)
def update_page_size(page_size):
    return page_size


@app.callback(
    Output(component_id="km-estimate-overall", component_property="figure"),
    [
        Input(component_id="show-conf-checkbox-overall", component_property="value"),
        Input(component_id="show-overall-median-time", component_property="value"),
    ]
)
def update_kmf_overall(show_conf, show_median):
    durations = data.t.values
    events = data.status.values
    plots = [(durations, events, "Overall")]
    limits = [0, 40, 0, 1]
    figure, kmf_results = plot_kmf(
        plots=plots, limits=limits, show_conf=show_conf, show_median=show_median
    )
    return figure


@app.callback(
    Output(component_id="km-estimate-treatments", component_property="figure"),
    [
        Input(component_id="show-conf-checkbox-treatments", component_property="value"),
        Input(component_id="show-medians", component_property="value")
    ]
)
def update_kmf_treatments(show_conf, show_median):
    plots = []
    for treatment_id in [0, 1]:
        treatment = data[data["Rx"] == treatment_id]
        durations = treatment.t.values
        events = treatment.status.values
        plots.append((durations, events, f"treatment_{treatment_id}"))
    limits = [0, 40, 0, 1]
    figure, kmf_results = plot_kmf(
        plots=plots, limits=limits, show_conf=show_conf, show_median=show_median
    )
    return figure


@app.callback(
    [
        Output('survival-subplots', 'figure'),
        Output('survival-subplots', 'style'),
    ],
    [
        Input('survival-dropdown', 'value'),
        Input(component_id="show-conf-subplots", component_property="value"),
        Input(component_id="show-medians-subplots", component_property="value")
    ]
)
def update_subplots(values, show_conf, show_median):
    n_rows = 2 if len(values) > 2 else 1
    height = f"{n_rows * 400}px"

    fig = make_subplots(
        rows=n_rows, cols=2,
        subplot_titles=values
    )

    subplots_info = [
        {"sex_name": "Male", "sex_id": 0, "treatment": 0},
        {"sex_name": "Male", "sex_id": 0, "treatment": 1},
        {"sex_name": "Female", "sex_id": 1, "treatment": 0},
        {"sex_name": "Female", "sex_id": 1, "treatment": 1},
    ]

    for n, value in enumerate(values):
        sex_name = subplots_info[n]["sex_name"]
        sex_id = subplots_info[n]["sex_id"]
        treatment = subplots_info[n]["treatment"]
        value = f"{sex_name}, treatment {treatment}"

        by_sex = data[data["sex"] == sex_id]
        by_treatment_and_sex = by_sex[by_sex["Rx"] == treatment]
        durations = by_treatment_and_sex.t.values
        events = by_treatment_and_sex.status.values
        subplots_kmf(
            fig=fig,
            row=sex_id,
            col=treatment,
            durations=durations,
            events=events,
            label=value,
            show_conf=show_conf,
            show_median=show_median
        )
    fig.update_xaxes(range=[0, 40])
    fig.update_yaxes(range=[0, 1])
    return fig, {"height": height}


if __name__ == "__main__":
    app.run_server(host="127.0.0.1", debug=True)
