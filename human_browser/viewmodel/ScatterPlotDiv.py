
from typing import Any
from functools import reduce
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import (ALL, MATCH, Input, Output, Patch, State, callback,
                  callback_context, dcc)
from dash.exceptions import PreventUpdate
import plotly.express as px
from plotly.graph_objs import Layout

from human_browser.backend.human_dataset import human_datasets
from human_browser.viewmodel.FigureDiv import FigureDiv

CELL_META_CLIP_INFO = """
**Cell ID**: {cell_id} ({assay})

**Brain Sample**:
- **Anatomy**: {_Region}

**Cell Annotation**:
- **Cell Class**: {_CellClass}
- **Cell SubClass**: {cell_type}
- **Cell Group**: {_MajorType}
"""

class ScatterPlotDiv(FigureDiv):
    '''
        Implementation for ScatterPlot.
    '''
    FigureString = "Scatterplot"

    @classmethod
    def _generate_graph_panel(cls, figure_json):
        datasource = figure_json.get("datasource", None)
        colorby = figure_json.get("colorby", None)
        coord = figure_json.get("coord", None)
        if coord is None or datasource is None or colorby is None:
            print("Missing parameter in figure_json")
            raise PreventUpdate

        dataframe = human_datasets[datasource].get_plot_data(coord, var_dict={datasource:colorby})
        print(dataframe.head())
        fig = cls._get_scatter_plot(dataframe, datasource, coord, colorby)

        panel_index = figure_json["panel_index"]
        figure_index = figure_json["figure_index"]
        layout = dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id={"type": "scatterplot-graph", "figure-index": figure_index, "panel-index": panel_index},
                            config=cls._DEFAULT_GRAPH_CONFIG,
                            figure=fig,
                        ),
                    ]
                ),
            ]
        )
        return layout

    @classmethod
    def _get_scatter_plot(cls, dataframe, datasource, coord, colorby):
        fig = px.scatter(data_frame=dataframe, x=f"{coord}_0", y=f"{coord}_1",
                         color=f"{datasource}:{colorby}", 
                         height=400)
        fig.update_coloraxes(showscale=False)
        fig.update(layout_showlegend=False)
        fig.update_layout(
            Layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis={"visible": False},
                yaxis={"visible": False},
            )
        ),
        return fig

    @callback(
        Output({"type": "scatterplot-graph", "figure-index": MATCH, "panel-index": MATCH}, "figure"),
        Input({"type": "control-scatterplot-update-button", "figure-index": MATCH, "panel-index": MATCH}, "n_clicks"),
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

    @callback(
        Output({"type": "clickdata-textarea", "panel-index": MATCH}, "children"),
        Output({"type": "scatterplot-graph", "figure-index": ALL, "panel-index": MATCH}, "clickData"),
        Input({"type": "scatterplot-graph", "figure-index": ALL, "panel-index": MATCH}, "clickData"),
        prevent_initial_call=True,
    )
    def showClickData(click_scatterplot_data):
        """React to click data, callback from clickData to the textbox"""
        num_scatterplot_graph = len(click_scatterplot_data)
        # print("Cont data", click_cont_data)
        # print("Cat data", click_cat_data)

        # find the non-none click data
        click_data = reduce(lambda a, b: a or b, click_scatterplot_data)
        print(click_data)
        point = click_data["points"][0]
        # x_value = point["x"]
        # y_value = point["y"]

        cell_int_id = point["pointIndex"]
        dataset = human_datasets['mCH_Inhi']
        cell_id = dataset._int_id_to_original_id[cell_int_id]
        use_meta_names = [
            "cell_id",
            "assay",
            "_Region",
            "_CellClass",
            "cell_type",
            "_MajorType",
        ]
        meta_dict = {k: dataset.get_metadata(k).loc[cell_id] for k in use_meta_names}
    
        # text = f"Clicked point: x={x_value}, y={y_value}"
        text = CELL_META_CLIP_INFO.format(**meta_dict)
        # Here we returned two sets of None to clear the click-data, so that we
        # can know what is the newly-click data for each click. This genius solution is posted
        # here: https://community.plotly.com/t/is-there-a-way-to-clear-clickdata/8708/10
        return text, [None] * num_scatterplot_graph
