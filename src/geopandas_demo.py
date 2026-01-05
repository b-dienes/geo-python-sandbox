"""
Main module for geospatial practice with GeoPandas.

Includes functions for:
- Resolving input file paths
- Loading GeoDataFrames
- Cleaning and validating geometries

This module is intended for daily geospatial exercises with US National Parks data.
"""

import logging
from pathlib import Path
import geopandas as gpd
from utils.paths import get_input_path, get_output_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def load_input_path():
    """
    Resolve the path to the input GeoPackage file.

    Returns
    -------
    Path
        Full path to the GeoPackage file containing US National Parks units.
    """
    file_path = get_input_path("us_nps_units_parks.gpkg")
    logger.info("Path resolved")
    return file_path

def read_gdf(file_path):
    """
    Load a GeoDataFrame from a given file path.

    Parameters
    ----------
    file_path : str or Path
        Path to the GeoPackage or other geospatial file.

    Returns
    -------
    gpd.GeoDataFrame
        Loaded GeoDataFrame.
    """
    gdf = gpd.read_file(file_path)
    logger.info(f"GeoDataFrame loaded: {file_path}")
    return gdf

def clean_gdf(gdf):
    """
    Validate and clean a GeoDataFrame.

    Checks performed:
    - GeoDataFrame is not empty
    - No null geometries
    - CRS is defined
    - Geometries are valid (invalid geometries are fixed)

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to clean and validate.

    Returns
    -------
    gpd.GeoDataFrame
        Cleaned and validated GeoDataFrame.
    
    Raises
    ------
    ValueError
        If the GeoDataFrame is empty, has null geometries, or no CRS.
    """
    if gdf.empty:
        raise ValueError("Gdf is empty")

    if gdf.geometry.isnull().any():
        raise ValueError("Empty geometry")

    if gdf.crs is None:
        raise ValueError("No CRS")
    else:
        logger.info(f"CRS: {gdf.crs.to_string()}")

    if not gdf.geometry.is_valid.all():
        gdf["geometry"] = gdf.geometry.make_valid()
        logger.info(f"Some geometries were invalid, now made valid")
    else:
        logger.info(f"All geometries were valid")

    logger.info(f"Fields: {gdf.columns}")

    return gdf


if __name__ == "__main__":
    file_path = load_input_path()
    gdf = read_gdf(file_path)
    cleaned_gdf = clean_gdf(gdf)



# TODO: CRS and projections
# TODO: Geometric operations
# TODO: Filtering & attributes
# TODO: Spatial joins & overlays
# TODO: Visualization