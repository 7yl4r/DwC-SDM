import pandas as pd
import rasterio
import xarray as xr
import numpy as np
from typing import Union, List, Tuple, Optional, Dict

def add_environmental_data(
    df: pd.DataFrame,
    raster_path: str,
    column_name: str = 'temperature',
    lat_col: str = 'decimalLatitude',
    lon_col: str = 'decimalLongitude'
) -> pd.DataFrame:

    df_result = df.copy()

    # TODO: change to use xarray
    with rasterio.open(raster_path) as src:
        coords = [(row[lon_col], row[lat_col]) for _, row in df.iterrows()]
        sampled_values = list(src.sample(coords))
        band_index = 0  # 0 is surface
        values = [val[band_index] if val[band_index] != src.nodata else np.nan for val in sampled_values]
        df_result[column_name] = values

    print(f"Added {column_name}: {df_result[column_name].notna().sum()}/{len(df_result)} valid values")
    return df_result
