"""
Main module for geospatial practice with GeoPandas.

Includes functions for:
- Resolving input file paths
- Loading GeoDataFrames
- Cleaning and validating geometries
- Reprojecting to pre-defined CRS

This module is intended for daily geospatial exercises with:
    US National Parks data: https://irma.nps.gov/DataStore/
    California state boundary data: https://data.ca.gov/dataset/
"""

import logging
from pathlib import Path
import geopandas as gpd
from pyproj import CRS
from utils.paths import get_input_path, get_output_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def load_input_path(filename: str) -> Path:
    """
    Resolve the path to the input GeoPackage file.

    Returns
    -------
    Path
        Full path to the GeoPackage file containing US National Parks units.
    """
    file_path = get_input_path(filename)
    logger.info("Path resolved")
    return file_path

def load_gdf(file_path: Path) -> gpd.GeoDataFrame:
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
    logger.info("GeoDataFrame loaded: %s", file_path)
    return gdf

def clean_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
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
        raise ValueError("Gdf is empty (has 0 records)")

    if gdf.geometry.isnull().any():
        raise ValueError("Has None in geometry")

    if gdf.geometry.is_empty.any():
        raise ValueError("Contains empty geometry")

    if gdf.crs is None:
        raise ValueError("No CRS")
    else:
        logger.info("CRS: %s", gdf.crs.to_string())

    gdf = gdf.copy()

    if not gdf.geometry.is_valid.all():
        gdf["geometry"] = gdf.geometry.make_valid()
        logger.info("Some geometries were invalid, now made valid")
    else:
        logger.info("All geometries were valid")

    logger.info("Fields: %s", gdf.columns)

    return gdf

def reproject_gdf(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:

    logger.info("Entered reprojection with %s", gdf.crs)

    target = CRS.from_user_input(target_crs)

    if gdf.crs != target:
        gdf = gdf.to_crs(target)
        logger.info("Reprojected to %s", gdf.crs)
    else:
        logger.info("Projection already in %s" ,gdf.crs)

    return gdf

if __name__ == "__main__":

    parks = "us_nps_units_parks.gpkg"
    state = "california_state_boundary.gpkg"
    target_crs = 'EPSG:5070'

    file_path = load_input_path(state)
    gdf = load_gdf(file_path)
    cleaned_gdf = clean_gdf(gdf)
    reprojected_gdf = reproject_gdf(cleaned_gdf, target_crs)


# TODO: CRS and projections
# TODO: Geometric operations
# TODO: Filtering & attributes
# TODO: Spatial joins & overlays
# TODO: Visualization