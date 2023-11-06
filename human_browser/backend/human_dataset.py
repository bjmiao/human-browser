import os

import pandas as pd
import scanpy

from .dataset import Dataset

DEFAULT_DATA_FOLDER = "/home/bmiao/human-browser-data"
ALL_DATASOURCE = {
    dataname: os.path.join(DEFAULT_DATA_FOLDER, dataname + ".h5ad")
    for dataname in ["mCG_Exhi", "mCG_Inhi", "mCG_Nonneuron", "mCH_Exhi", "mCH_Inhi", "mCG_Nonneuron"]
}
HUMAN_METADATA_PATH = "/home/bmiao/human-browser-data/celltype_snmc.csv.gz"


class HumanDataset(Dataset):
    """Human Dataset"""

    def __init__(self, name: str, filename: str) -> None:
        self.dataset_handle = scanpy.read_h5ad(filename, backed="r")
        # df_cellmeta = pd.read_csv(HUMAN_METADATA_PATH)
        # df_cellmeta = df_cellmeta.rename(columns={"Unnamed: 0": "cell"})
        # df_cellmeta.set_index("cell")
        df_cellmeta = self.dataset_handle.obs
        df_cellmeta["cell_id"] = df_cellmeta.index
        super().__init__(name=name, obs_ids=df_cellmeta.index, obs_dim="cell")
        self.add_metadata_df(df_cellmeta)

        coords = ["umap", "tsne"]
        for coord in coords:
            self.add_coords(
                coord, pd.DataFrame(self.dataset_handle.obsm["X_" + coord], index=self.dataset_handle.obs.index)
            )

        self._var_matrices[name] = self.dataset_handle

    def get_var_values(self, set_name: str, var_name: str) -> pd.Series:
        """
        Get a series of values for a given variable in a given feature set.

        This is an override of the base class, since we are not using xarray here but using
        AnnData instead.
        """
        try:
            _da = self._var_matrices[set_name]
        except KeyError:
            raise KeyError(f"Feature set '{set_name}' not found.")
        print(self.metadata_names)
        print("DDX11L1" in _da.var.feature_name.values)
        print(var_name)
        if var_name in _da.var.index:  # "ENSG00000223972"
            _data = _da[:, var_name].to_df()
        elif var_name in _da.var.feature_name.values:  # "DDX11L1"
            _data = _da[:, _da.var.feature_name == var_name].to_df()
        elif var_name in self.metadata_names:
            _data = self._metadata[var_name]
        else:
            try:
                # try a default indexing as the safety net
                _data = _da[:, var_name].to_df()
            except KeyError:
                raise KeyError(f"Variable '{var_name}' not found in feature set '{set_name}'.")

        print(_data)
        print(type(_data))
        if _data.index.name not in {self.obs_dim, "obs"}:
            # map data to cell level
            _data = self.get_metadata(_data.index.name).map(_data)
        return _data


human_datasets = {name: HumanDataset(name, datapath) for name, datapath in ALL_DATASOURCE.items()}
