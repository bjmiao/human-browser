import os

import pandas as pd
import plotly.express as px
import scanpy
from dash.exceptions import PreventUpdate

DEFAULT_DATA_PATH = "C:\\Users\\bimia\\Documents\\Workspace\\eckarlab_rotation_20230928\\browser_sample_data\\"


def get_scatter_from_precompute_result(datasource, coord, color_type, colorby):
    """Generate a plot from local file.

    Arguments:
    datasource: filename as the dataset.
    -- it should be a h5ad file, and contains the following fields:
    ---- obs: {colorby}
    ---- obsm: X_{coord}
    colortype: categorical or continuous
    coord: coordinates of the scattering, umap or tsne now
    colorby: coloring result

    Returns: a Figure object
    """
    filename = os.path.join(DEFAULT_DATA_PATH, datasource + ".h5ad")

    try:
        dataset = scanpy.read_h5ad(filename, backed="r")
    except FileNotFoundError as e:
        print(e)
        import traceback as tb

        tb.print_stack()
        raise PreventUpdate

    coord_field = "X_" + coord
    coord_data = dataset.obsm[coord_field]
    X = coord_data[:, 0]
    Y = coord_data[:, 1]

    color_value = None
    # TODO: add colormap or palette with scientific meaning
    if color_type == "continuous":
        color_value = dataset.obs[colorby]
    elif color_type == "categorical":
        color_set = dataset.obs[colorby].unique()
        color_map = {color: index for index, color in enumerate(color_set)}
        color_value = [color_map[x] for x in dataset.obs[colorby]]

    df = pd.DataFrame({"x": X, "y": Y, "color": color_value})
    fig = px.scatter(data_frame=df, x="x", y="y", color="color")
    return fig
