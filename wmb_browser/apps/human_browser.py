import json

import dash_bootstrap_components as dbc
from dash import Input, Output, Patch, State, callback, html
from dash.exceptions import PreventUpdate

from wmb_browser.viewmodel import CategoricalFigurePanel, ContinuousFigurePanel

DEMO_TEXT = """
{"coord": "tsne", "datasource": "local",
    "figures": [
        {"type": "continuous", "colorby": "_Region"},
        {"type": "categorical", "colorby": "_mCGFrac"}
    ]
}
"""
input_div = html.Div(
    [
        dbc.Container([html.H1("Select Dissection and Gene for scatter plot")]),
        dbc.Container(
            [
                dbc.Col(
                    dbc.Textarea(id="new-item-input", style={"height": 100}, value=DEMO_TEXT),
                    className="mb-1",
                    xxl=10,
                    xl=10,
                    lg=8,
                    md=6,
                    sm=12,
                ),
                dbc.Col(dbc.Button("Add Figure", className="my-1 mr-2", outline=True, size="sm", id="add-figure")),
            ]
        ),
    ]
)


def _generate_figure_div(input_string, panel_index):
    """Generate a figure.

    Args:
        input_string should be lines of JSON strings indicating
            what type of plots should be generated
    Returns:
        success: True or false, whether this add-figure succeed
        figure_div: the Div for the figure
    """
    figure_json = None
    try:
        figure_json = json.loads(input_string)
    except json.decoder.JSONDecodeError as e:
        print(e)
        raise PreventUpdate
    figure_container = None
    # figure_types = figure_json['type']
    # if type(figure_types) == str: # only one type:
    #     figure_type = [figure_types]
    figure_all = figure_json["figures"]
    if type(figure_all) is dict:
        figure_all = [figure_all]
    if len(figure_all) > 10:
        print("Too much figures at the same time")
        raise PreventUpdate
    all_figures = []
    for figure_index, figure_config in enumerate(figure_all):
        figure_type = figure_config["type"]
        figure_json_single_figure = figure_json.copy()
        figure_json_single_figure.pop("figures")
        figure_json_single_figure["panel_index"] = panel_index
        figure_json_single_figure["figure_index"] = figure_index
        figure_json_single_figure["figure_type"] = figure_type
        for k, v in figure_config.items():
            figure_json_single_figure[k] = v
        print(figure_json_single_figure)
        if figure_type == "continuous":
            figure_container = ContinuousFigurePanel.generate_panel(figure_json_single_figure)
            # generate_continuous_figure(figure_json)
            all_figures.append(figure_container)
        elif figure_type == "categorical":
            figure_container = CategoricalFigurePanel.generate_panel(figure_json_single_figure)
            # figure_container = generate_categorical_figure(figure_json)
            all_figures.append(figure_container)
        elif figure_type == "higlass":
            pass
        else:
            print(f"Unknown figure type {figure_type}. This panel will not be shown")

    panel_wrapper = dbc.Container([dbc.Row([dbc.Col([figure]) for figure in all_figures])])

    return True, panel_wrapper


@callback(
    Output("figure-div", "children", allow_duplicate=True),
    Input("add-figure", "n_clicks"),
    State("new-item-input", "value"),
    prevent_initial_call=True,
)
def add_figure(n_clicks, input_string):
    """Add a figure given the input string

    Args:
    - n_clicks: used as the panel index (1-based)
    - input_string: should be in a json format
    Returns:
    - a panel of figure in a Div
    """
    if not n_clicks:
        raise PreventUpdate
    # updated_localstorage = Patch()
    # updated_localstorage['data'] = localstorage + [input_string]

    # get this div
    success, new_figure_div = _generate_figure_div(input_string, panel_index=n_clicks)
    updated_figure_div = Patch()
    if success:
        updated_figure_div.append(new_figure_div)
    else:
        raise PreventUpdate
    return updated_figure_div


def initial_human_browser_layout():
    """Dynamically initialized the browser layout"""
    human_browser_layout = html.Div(
        [
            input_div,
            html.Div(id="figure-div", children=[], className="row"),  # place to show all figures
            # TODO: how to load the localstorage when initiating the page
            # html.Div(id='hover-data', children=[])
            # html.Div([dcc.Store(id='figure-string-localstorage', storage_type='local', data='''''')]) # used to cache the panels
        ]
    )
    return human_browser_layout
