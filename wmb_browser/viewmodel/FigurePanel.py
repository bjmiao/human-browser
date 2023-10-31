import dash_bootstrap_components as dbc
from dash import dcc, html


class FigurePanel(object):
    """The (abstract) bass class for the single figure panel"""

    FigureString = "Figure"
    _DEFAULT_GRAPH_CONFIG = {
        "scrollZoom": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["select", "select2d", "autoScale"],
        "toImageButtonOptions": {
            "format": "png",  # one of png, svg, jpeg, webp
            "filename": "custom_image",
            "scale": 4,  # Multiply title/legend/axis/canvas sizes by this factor
        },
    }

    def __init__(self):
        pass

    @classmethod
    def _generate_graph_panel(cls, figure_json):
        """Generate the actual plotting"""
        print("why here")
        return None

    @classmethod
    def _generate_control_panel(cls, figure_json):
        """Generate the control tab"""
        print("why here")
        return None

    @classmethod
    def _generate_text_description_layout(cls, figure_type, panel_index, figure_index):
        text_description_layout = html.Div(
            [
                dcc.Markdown("""
                **Click Data**

                Click on points in the graph.
            """),
                # html.Pre(/id='click-data'),
                html.Pre(
                    id={
                        "type": f"{figure_type}-click-data",
                        "panel-index": panel_index,
                        "figure-index": figure_index,
                    }
                ),
                dcc.Clipboard(
                    # target_id='click-data',
                    target_id={
                        "type": f"{figure_type}-click-data",
                        "panel-index": panel_index,
                        "figure-index": figure_index,
                    },
                    title="copy",
                    style={
                        "display": "inline-block",
                        "fontSize": 20,
                        "verticalAlign": "top",
                    },
                ),
            ],
            className="three columns",
        )
        return text_description_layout

    @classmethod
    def generate_panel(cls, figure_json):
        """Generate a single panel, as the entrance function"""
        figure_type = figure_json.get("figure_type", None)
        panel_index = figure_json.get("panel_index", -1)
        figure_index = figure_json.get("figure_index", -1)
        if figure_type is None or panel_index == -1 or figure_index == -1:
            raise ValueError("Panel index or figure index not indicated")
        # set up the graph label
        coord = figure_json.get("coord", "")
        colorby = figure_json.get("colorby", "")
        graph_label = figure_json.get("label", f"{figure_type}_{coord}_{colorby}")
        cls._generate_text_description_layout(figure_type, panel_index, figure_index)
        graph = cls._generate_graph_panel(figure_json)
        # graph_tab = [dbc.Row([dbc.Col([graph])]), dbc.Row([dbc.Col([graph_text_description])])]
        graph_tab = [dbc.Row([dbc.Col([graph])])]

        graph_controls = cls._generate_control_panel(figure_json)
        tabs = dbc.Col(
            dbc.Tabs(
                [
                    dbc.Tab(graph_tab, label=graph_label),
                    dbc.Tab(graph_controls, label="Control"),
                ]
            ),
            class_name="mt-3",
        )
        return tabs
