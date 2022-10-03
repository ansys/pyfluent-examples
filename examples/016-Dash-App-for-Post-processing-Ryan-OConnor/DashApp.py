# import modules
import os

import CreatePPTX
import ansys.fluent.core as pyfluent
import dash
from dash import Input, Output, State, dash_table, dcc, html
import dash_bootstrap_components as dbc

# Launch fluent
session = pyfluent.launch_fluent(mode="solver")
tabularData = []

# Read case file
session.tui.file.read_case_data("elbow.cas.h5")

if os.path.exists("transcript.txt"):
    os.remove("transcript.txt")

# Start session transcript
session.tui.file.start_transcript("transcript.txt")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = dbc.Container(
    [
        html.H1("Pipe Elbow Dash App", className="mt-3"),
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Ul(
                                children=[
                                    html.Li(
                                        "Define inlet temperature and velocity for main and side inlets, "  # noqa: E501
                                        "select fluid material, and number of iterations."  # noqa: E501
                                    ),
                                    html.Li(
                                        'Enable "Initialize" to (re)initialize the solution before iterating.'  # noqa: E501
                                    ),
                                    html.Li('Click "Solve" to iterate.'),
                                    html.Li(
                                        'Click "View Report" to generate and display a Simulation Report.'  # noqa: E501
                                    ),
                                    html.Li(
                                        'Click "Download PowerPoint Report" to generate and save a PPTX.'  # noqa: E501
                                    ),
                                ]
                            )
                        ]
                    ),
                    dbc.Col(
                        [
                            html.Img(
                                src="ImgMesh.jpg",
                                height=250,
                                style={
                                    "display": "block",
                                    "margin-left": "auto",
                                    "margin-right": "auto",
                                },
                            )
                        ]
                    ),
                ],
                style={"margin": "20px"},
            ),
        ),
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Main Inlet - Temperature [Kelvin]"),
                            dcc.Slider(
                                250,
                                350,
                                5,
                                id="main_in_temp",
                                value=300,
                                marks={i: "{}".format(i) for i in range(250, 370, 20)},
                            ),
                            dbc.Label("Main Inlet - Velocity"),
                            dcc.Slider(
                                0.0,
                                1.0,
                                0.1,
                                id="main_in_vel",
                                value=0.5,
                                marks={
                                    0: "0.0",
                                    0.2: "0.2",
                                    0.4: "0.4",
                                    0.6: "0.6",
                                    0.8: "0.8",
                                    1: "1.0",
                                },
                            ),
                            dbc.Label("Material", html_for="dropdown"),
                            dcc.Dropdown(
                                id="material",
                                options=[
                                    {"label": "water", "value": "water-liquid"},
                                    {"label": "air", "value": "air"},
                                ],
                                value="water-liquid",
                                clearable=False,
                            ),
                            html.Div(
                                [
                                    dcc.Checklist(
                                        ["Initialize"], ["Initialize"], id="initialize"
                                    )
                                ],
                                style={"margin-top": "10px"},
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Label("Side Inlet - Temperature [Kelvin]"),
                            dcc.Slider(
                                250,
                                350,
                                5,
                                id="side_in_temp",
                                value=300,
                                marks={i: "{}".format(i) for i in range(250, 370, 20)},
                            ),
                            dbc.Label("Side Inlet - Velocity"),
                            dcc.Slider(
                                0.0,
                                1.0,
                                0.1,
                                id="side_in_vel",
                                value=0.5,
                                marks={
                                    0: "0.0",
                                    0.2: "0.2",
                                    0.4: "0.4",
                                    0.6: "0.6",
                                    0.8: "0.8",
                                    1: "1.0",
                                },
                            ),
                            dbc.Label("Iterations"),
                            dcc.Slider(
                                5,
                                200,
                                5,
                                id="numberIts",
                                value=5,
                                marks={5: "5", 50: "50", 100: "100", 200: "200"},
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Button("Solve", id="solve_button"),
                            dbc.Button("View Report", id="viewReport_button"),
                            dbc.Button(
                                "Download PowerPoint Report", id="downloadPPTX_button"
                            ),
                            dcc.Download(id="download-pptx"),
                            dcc.Loading(
                                id="loading-1",
                                type="default",
                                children=html.Div(id="loading-output-1"),
                                style={"margin-top": "40px"},
                            ),
                            dcc.Loading(
                                id="loading-2",
                                type="default",
                                children=html.Div(id="loading-output-2"),
                                style={"margin-top": "40px"},
                            ),
                            dcc.Loading(
                                id="loading-3",
                                type="default",
                                children=html.Div(id="loading-output-3"),
                                style={"margin-top": "40px"},
                            ),
                        ],
                        style={"height": "80%", "width": "30%"},
                        className="d-grid gap-2 col-6 mx-auto",
                    ),
                ],
                style={"margin": "20px"},
            ),
            style={"margin-top": "20px"},
        ),
        dbc.Card(
            dbc.CardBody(
                html.Div(
                    [
                        html.B("History of Simulations"),
                        dash_table.DataTable(
                            id="tableData",
                            columns=[
                                {"name": "Main Inlet Temp (K)", "id": "MITtable"},
                                {"name": "Main Inlet Vel (m/s)", "id": "MIVtable"},
                                {"name": "Side Inlet Temp (K)", "id": "SITtable"},
                                {"name": "Side Inlet Vel (m/s)", "id": "SIVtable"},
                                {"name": "Material", "id": "MATtable"},
                                {"name": "Ave Outlet Temp (K)", "id": "AOTtable"},
                            ],
                            style_data_conditional=[
                                {
                                    "font-family": "Helvetica, Arial, " "sans-serif",
                                    "text-align": "center",
                                }
                            ],
                            style_header_conditional=[
                                {
                                    "font-family": "Helvetica, Arial, " "sans-serif",
                                    "text-align": "center",
                                }
                            ],
                        ),
                    ]
                )
            ),
            style={"margin-top": "20px"},
        ),
        dbc.Card(
            dbc.CardBody(
                html.Div(
                    [
                        dcc.Tabs(
                            id="tabs-example-graph",
                            value="tab-1-report",
                            children=[
                                dcc.Tab(label="Report", value="tab-1-report"),
                                dcc.Tab(
                                    label="Fluent Transcript", value="tab-2-transcript"
                                ),
                            ],
                        ),
                        html.Div(
                            id="tabs-content-example-graph",
                            style={"overflow-y": "scroll", "height": "800px"},
                        ),
                    ]
                ),
            ),
            style={"margin-top": "20px"},
        ),
    ]
)


@app.callback(
    Output("tableData", "data"),
    Output("loading-output-1", "children"),
    Input("solve_button", "n_clicks"),
    State("material", "value"),
    State("main_in_temp", "value"),
    State("main_in_vel", "value"),
    State("side_in_temp", "value"),
    State("side_in_vel", "value"),
    State("numberIts", "value"),
    State("initialize", "value"),
    Prevent_initial_call=True,
)
def Solve(
    n_clicks,
    material,
    main_in_temp,
    main_in_vel,
    side_in_temp,
    side_in_vel,
    numberIts,
    initialize,
):
    if (
        n_clicks
    ):  # This if statement is required since Prevent_initial_call is not working
        if initialize:
            session.solution.initialization.standard_initialize()
        session.setup.cell_zone_conditions.fluid["fluid"].material = material
        session.setup.boundary_conditions.velocity_inlet[
            "cold-inlet"
        ].vmag.value = main_in_vel
        session.setup.boundary_conditions.velocity_inlet[
            "hot-inlet"
        ].vmag.value = side_in_vel
        session.setup.boundary_conditions.velocity_inlet["cold-inlet"].t = main_in_temp
        session.setup.boundary_conditions.velocity_inlet["hot-inlet"].t = side_in_temp
        session.solution.run_calculation.iterate(iter_count=numberIts)
        outlet_temp = session.solution.report_definitions.compute(
            report_defs=["avg-outlet-temp"]
        )[0]["avg-outlet-temp"][0]
        tabularData.append(
            {
                "MITtable": main_in_temp,
                "MIVtable": main_in_vel,
                "SITtable": side_in_temp,
                "SIVtable": side_in_vel,
                "MATtable": material,
                "AOTtable": outlet_temp,
            }
        )
    return tabularData, ""


@app.callback(
    Output("report_display", "src"),
    Output("loading-output-2", "children"),
    Input("viewReport_button", "n_clicks"),
    Prevent_initial_call=True,
)
def ShowReport(n_clicks):
    reportLink = ""
    if (
        n_clicks
    ):  # This if statement is required since Prevent_initial_call is not working
        if os.path.exists("index.html"):
            os.remove("index.html")
        session.tui.report.simulation_reports.generate_simulation_report("SimRep")
        session.tui.report.simulation_reports.export_simulation_report_as_html("SimRep")
        reportLink = "index.html"
        print(reportLink)
    return reportLink, ""


@app.callback(
    Output("download-pptx", "data"),
    Output("loading-output-3", "children"),
    Input("downloadPPTX_button", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    session.tui.display.set.picture.driver.jpeg()
    CreatePPTX.generatePPTX(session)
    return dcc.send_file("report.pptx"), ""


@app.callback(
    Output("tabs-content-example-graph", "children"),
    Input("tabs-example-graph", "value"),
)
def render_content(tab):
    if tab == "tab-1-report":
        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.Iframe(
                            id="report_display",
                            style={"height": "1067px", "width": "100%"},
                        ),
                        html.Div(
                            id="ryanoutput", style={"width": "100%", "height": "60vh"}
                        ),
                    ],
                    width=10,
                ),
            ],
            style={"margin-top": "20px"},
        )
    elif tab == "tab-2-transcript":
        file = open("transcript.txt")
        text = file.readlines()
        file.close()
        return html.Div(
            dcc.Markdown(text),
            style={"font-family": "Courier New, monospace", "font-size": "15px"},
        )


if __name__ == "__main__":
    app.run_server()
