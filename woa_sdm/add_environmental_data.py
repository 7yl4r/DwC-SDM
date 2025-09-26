import pandas as pd
import rasterio
from rasterio.fill import fillnodata
import numpy as np
from typing import Union, List, Tuple, Optional, Dict

def add_environmental_data(
    df: pd.DataFrame,
    raster_path: str,
    column_name: str = 'temperature',
    lat_col: str = 'decimalLatitude',
    lon_col: str = 'decimalLongitude',
    band: int = 1,
    max_search_distance: int = 100,
    smoothing_iterations: int = 0
) -> pd.DataFrame:
    """
    Sample a raster at point coordinates, filling NoData regions by interpolation first.

    Parameters
    ----------
    df : DataFrame with columns [lat_col, lon_col]
    raster_path : path to a GeoTIFF
    column_name : name for the output column
    lat_col, lon_col : column names for latitude/longitude (in raster CRS)
    band : 1-based band index to sample
    max_search_distance : pixels to search for valid neighbors when filling
    smoothing_iterations : post-fill smoothing iterations

    Returns
    -------
    DataFrame with a new column `column_name`.
    """
    df_result = df.copy()

    with rasterio.open(raster_path) as src:
        # Read band as a masked array (mask=True where NoData)
        arr = src.read(band, masked=True).astype("float32")

        print(f"[{band}] img.shape: {arr.shape}, img.ndim: {arr.ndim}")

        # Interpolate holes (where mask==True)
        # fillnodata uses 'mask' to identify holes; values in those cells are ignored.
        filled = fillnodata(
            arr.filled(0.0),      # actual values used where mask is False
            mask=arr.mask,        # holes to fill
            max_search_distance=max_search_distance,
            smoothing_iterations=smoothing_iterations
        )

        # Vectorized sampling by converting lon/lat to row/col
        lons = df_result[lon_col].to_numpy()
        lats = df_result[lat_col].to_numpy()

        # Pre-allocate output with NaN
        out = np.full(lons.shape, np.nan, dtype="float32")

        # Compute row/col per point and fetch values if inside bounds
        for i, (lon, lat) in enumerate(zip(lons, lats)):
            try:
                row, col = src.index(lon, lat)  # (row, col) for this lon/lat
                if 0 <= row < src.height and 0 <= col < src.width:
                    out[i] = filled[row, col]
                # else keep NaN (outside raster bounds)
            except Exception:
                # keep NaN if transform fails (e.g., invalid coords)
                pass

        df_result[column_name] = out

    print(f"Added {column_name}: {np.isfinite(df_result[column_name]).sum()}/{len(df_result)} valid values")
    return df_result
