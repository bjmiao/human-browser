import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from wmb_browser.backend.higlass_dash import higlass

higlass_examples = {
    "Multi-2D Higlass": (
        "higlass,multi_cell_type_2d,cell_types=CA3 Glut+Sst Gaba,region1=chr1:11000000-12000000",
        "info",
    ),
    "Multi-1D Higlass": (
        "higlass,multi_cell_type_1d,cell_types=CA3 Glut+Sst Gaba,region=chr1:11000000-12000000",
        "info",
    ),
    "Diff Compare Higlass": (
        "higlass,two_cell_type_diff,cell_type_1=CA3 Glut,cell_type_2=Sst Gaba,region1=chr1:10000000-13000000",
        "info",
    ),
    "2D Zoom-in Higlass": (
        (
            "higlass,loop_zoom_in,cell_type=CA3"
            " Glut,region1=chr1:10000000-13000000,zoom_region1=chr1:11550000-11720000,zoom_region2=chr1:12710000-12910000"
        ),
        "info",
    ),
}

def _string_to_args_and_kwargs(string):
    string = string.strip(" ?,")
    args = []
    kwargs = {}
    for text in string.split(","):
        text = text.strip()
        kv = text.split("=")
        if len(kv) == 1:
            args.append(text)
        elif len(kv) == 2:
            kwargs[kv[0]] = kv[1]
        else:
            raise ValueError(f"Cannot parse {text}")

    # assume the first arg is dataset
    dataset, plot_type, *args = args

    # if dataset not in ALL_DATASETS:
    #     raise ValueError(f"Unknown dataset {dataset}")
    # if plot_type not in ALL_PLOT_TYPES:
    #     raise ValueError(f"Unknown plot type {plot_type} for dataset {dataset}")

    return dataset, plot_type, args, kwargs

string, aux = higlass_examples["2D Zoom-in Higlass"]

def _make_graph_from_string(i, string, use_gpt=False):
    graph = None
    graph_controls = None

    dataset, plot_type, args, kwargs = _string_to_args_and_kwargs(string)
    final_string = f"{dataset},{plot_type}"
    if len(args) > 0:
        final_string += f",{','.join(args)}"
    if len(kwargs) > 0:
        final_string += f",{','.join([f'{k}={v}' for k, v in kwargs.items()])}"
    try:
        graph, graph_controls = higlass.get_higlass_and_control(index=i, layout=plot_type, *args, **kwargs)
    except Exception as e:
        print(f"Error when plotting {plot_type} for dataset {dataset}")
        print(e)

    return graph, graph_controls, dataset, plot_type, final_string

graph, graph_controls, dataset, plot_type, final_string = _make_graph_from_string(1, string)


# from higlass.client import View, Track
# import higlass
# from collections import defaultdict

# all_tracks = defaultdict(list)


# view1 = higlass.view([
#     higlass.track(type_='top-axis', position='top'),
#     higlass.track(type_='heatmap', position='center',
#           tileset_uuid='CQMd6V_cRw6iCI_-Unl3PQ',
#           server="http://higlass.io/api/v1/",
#           height=250,
#           options={ 'valueScaleMax': 0.5 }),
# ])

# display, server, viewconf = higlass.display([view1])
# print(type(display))

higlass_demo_layout = html.Div([
    dbc.Col(
        dbc.Tabs(
            [
                dbc.Tab(graph, label='111'),
                # dbc.Tab(display, label='111'),
                dbc.Tab(graph_controls, label="Control"),
            ]
        ),
        class_name="mt-3",
    )
])
