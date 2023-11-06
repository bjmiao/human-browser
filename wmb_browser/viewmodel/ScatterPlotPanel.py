import dash_bootstrap_components as dbc
from dash import (ALL, MATCH, Input, Output, Patch, State, callback,
                  callback_context, dcc)
from dash.exceptions import PreventUpdate

from wmb_browser.datamodel.scatterplot import \
    get_scatter_from_precompute_result
from wmb_browser.viewmodel.FigureDiv import FigurePanel


@callback(
    Output({"panel-index": MATCH, "figure-index": ALL, "type": "continuous-graph"}, "figure", allow_duplicate=True),
    Output({"panel-index": MATCH, "figure-index": ALL, "type": "categorical-graph"}, "figure", allow_duplicate=True),
    Input({"panel-index": MATCH, "figure-index": ALL, "type": "continuous-graph"}, "relayoutData"),
    Input({"panel-index": MATCH, "figure-index": ALL, "type": "categorical-graph"}, "relayoutData"),
    prevent_initial_call=True,
)
def update_scatter_graph_relayout_data(cont_args, cat_args):
    """Syncronize the layout of graphs inside a panel when relayouting

    Args: All figures MATCH'ing in a panel
    Returns: Patches of those figures
    """
    trigger = callback_context.triggered[0]
    print(trigger)
    trigger_layout = trigger["value"]

    if "autosize" in trigger_layout:
        raise PreventUpdate
    else:
        try:
            xaxis_min = trigger_layout["xaxis.range[0]"]
            xaxis_max = trigger_layout["xaxis.range[1]"]
            yaxis_min = trigger_layout["yaxis.range[0]"]
            yaxis_max = trigger_layout["yaxis.range[1]"]
        except KeyError:
            raise PreventUpdate

    # # get coord for each index
    # idx_to_coord = {}
    # for state_dict in callback_context.inputs_list[0]:
    #     idx = state_dict["id"]["index"]
    #     coord = state_dict["value"]
    #     idx_to_coord[idx] = coord
    # trigger_coord = idx_to_coord[callback_context.triggered_id["index"]]

    cont_inputs, cat_inputs = callback_context.inputs_list
    cont_outputs, cat_outputs = [], []

    # print all states
    # print("cont_args", cont_args)
    # print("cat_args", cat_args)
    # print("coords", coords)
    # print("trigger", trigger)
    # print("trigger_layout", trigger_layout)
    print(cont_inputs, cat_inputs)
    for _input in cont_inputs:
        _p = Patch()
        # TODO: deploy relayout when ok
        # if cont_inputs["value"].get("xaxis.range[0]", None) is None:
        #     new_axis_lim = {""}
        # coord = idx_to_coord[input["id"]["index"]]
        # if coord == trigger_coord:
        _p["layout"]["xaxis"]["range"] = [xaxis_min, xaxis_max]
        _p["layout"]["yaxis"]["range"] = [yaxis_min, yaxis_max]
        cont_outputs.append(_p)

    for _input in cat_inputs:
        _p = Patch()
        # coord = idx_to_coord[input["id"]["index"]]
        # if coord == trigger_coord:
        _p["layout"]["xaxis"]["range"] = [xaxis_min, xaxis_max]
        _p["layout"]["yaxis"]["range"] = [yaxis_min, yaxis_max]
        cat_outputs.append(_p)
    print(cont_outputs, cat_outputs)
    return cont_outputs, cat_outputs


class ContinuousFigurePanel(FigurePanel):
    """Implementation of figure panel for continuous scatter plot"""

    FigureString = "ContinuousFigure"

    @classmethod
    def _generate_graph_panel(cls, figure_json):
        datasource = figure_json.get("datasource", None)
        colorby = figure_json.get("colorby", None)
        coord = figure_json.get("coord", None)
        if coord is None or datasource is None or colorby is None:
            print("Missing parameter in figure_json")
            raise PreventUpdate

        fig = get_scatter_from_precompute_result(
            datasource=figure_json["datasource"], color_type="continuous", colorby=colorby, coord=coord
        )

        panel_index = figure_json["panel_index"]
        figure_index = figure_json["figure_index"]
        layout = dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id={"type": "continuous-graph", "figure-index": figure_index, "panel-index": panel_index},
                            config=cls._DEFAULT_GRAPH_CONFIG,
                            figure=fig,
                        ),
                    ]
                ),
            ]
        )
        return layout
        # return super().generate_control_panel()

    @callback(
        Output({"type": "continuous-graph", "figure-index": MATCH, "panel-index": MATCH}, "figure"),
        Input({"type": "control-continuous-update-button", "figure-index": MATCH, "panel-index": MATCH}, "n_clicks"),
        State({"type": "control-color-range", "figure-index": MATCH, "panel-index": MATCH}, "value"),
        State({"type": "control-sample-number", "figure-index": MATCH, "panel-index": MATCH}, "value"),
        prevent_init_call=True,
    )
    def update_continuous_graph(nclicks, color_range, sample_number):
        """Load control tab parameter and update the graph"""
        print(nclicks, color_range, sample_number)
        new_figure = Patch()
        # new_figure = _generate_continuous_graph(sample_number, color_range)
        return new_figure

    @classmethod
    def _generate_control_panel(cls, figure_json):
        figure_type = figure_json["figure_type"]
        panel_index = figure_json["panel_index"]
        figure_index = figure_json["figure_index"]
        # range
        range_slider = dbc.Row(
            [
                dbc.Label("Color Range", width="auto"),
                dbc.Col(
                    dcc.RangeSlider(
                        id={
                            "type": "control-color-range",
                            "figure-index": figure_index,
                            "panel-index": panel_index,
                        },
                        min=0,
                        max=100,
                        value=[5, 10],
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3",
        )
        # sample control
        sample_control = dbc.Row(
            [
                dbc.Label("Downsample to", width="auto"),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        min=100,
                        max=5000,
                        step=1,
                        value=100,
                        id={"type": "control-sample-number", "figure-index": figure_index, "panel-index": panel_index},
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3",
        )
        update_button = dbc.Button(
            "Update",
            id={
                "figure-index": figure_index,
                "panel-index": panel_index,
                "type": f"control-{figure_type}-update-button",
            },
            outline=True,
            color="primary",
            n_clicks=0,
        )
        form = dbc.Form([range_slider, sample_control, update_button])
        return form


class CategoricalFigurePanel(FigurePanel):
    """Categorical scatter plot"""

    FigureString = "CategoricalFigure"

    @classmethod
    def _generate_graph_panel(cls, figure_json):
        datasource = figure_json.get("datasource", None)
        colorby = figure_json.get("colorby", None)
        coord = figure_json.get("coord", None)
        if coord is None or datasource is None or colorby is None:
            print("Missing parameter in figure_json")
            raise PreventUpdate

        fig = get_scatter_from_precompute_result(
            datasource=figure_json["datasource"], color_type="categorical", colorby=colorby, coord=coord
        )

        panel_index = figure_json["panel_index"]
        figure_index = figure_json["figure_index"]
        layout = dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id={"type": "categorical-graph", "panel-index": panel_index, "figure-index": figure_index},
                            config=cls._DEFAULT_GRAPH_CONFIG,
                            figure=fig,
                        ),
                    ]
                )
            ]
        )
        return layout
        # return super().generate_control_panel()

    @callback(
        Output({"type": "categorical-graph", "figure-index": MATCH, "panel-index": MATCH}, "figure"),
        Input({"type": "control-categorical-update-button", "figure-index": MATCH, "panel-index": MATCH}, "n_clicks"),
        State({"type": "control-color-range", "figure-index": MATCH, "panel-index": MATCH}, "value"),
        State({"type": "control-sample-number", "figure-index": MATCH, "panel-index": MATCH}, "value"),
        prevent_init_call=True,
    )
    def update_categorical_graph(nclicks, color_range, sample_number):
        """Do you hear the people sing? Singing the song of the angry man"""
        print(nclicks, color_range, sample_number)
        new_figure = Patch()
        # new_figure = _generate_categorical_graph(sample_number, color_range)
        return new_figure

    @classmethod
    def _generate_control_panel(cls, figure_json):
        figure_type = figure_json["figure_type"]
        panel_index = figure_json["panel_index"]
        figure_index = figure_json["figure_index"]
        # range
        range_slider = dbc.Row(
            [
                dbc.Label("Color Range", width="auto"),
                dbc.Col(
                    dcc.RangeSlider(
                        id={"type": "control-color-range", "figure-index": figure_index, "panel-index": panel_index},
                        min=0,
                        max=100,
                        value=[5, 10],
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3",
        )
        # sample control
        sample_control = dbc.Row(
            [
                dbc.Label("Downsample to", width="auto"),
                dbc.Col(
                    dbc.Input(
                        type="number",
                        min=100,
                        max=5000,
                        step=1,
                        value=100,
                        id={"type": "control-sample-number", "figure-index": figure_index, "panel-index": panel_index},
                    ),
                    className="me-3",
                ),
            ],
            className="g-2 mb-3",
        )
        update_button = dbc.Button(
            "Update",
            id={
                "type": f"control-{figure_type}-update-button",
                "figure-index": figure_index,
                "panel-index": panel_index,
            },
            outline=True,
            color="primary",
            n_clicks=0,
        )
        form = dbc.Form([range_slider, sample_control, update_button])
        return form
