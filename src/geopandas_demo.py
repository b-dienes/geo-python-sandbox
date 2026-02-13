"""
Validate and clean geometries, reproject to a user-defined CRS, log statistics.
Perform spatial clipping operations and quantifying area differences before and after clipping.

The module uses real-world public datasets:
- US NPS unit boundaries (filtered subset): https://irma.nps.gov/DataStore/
- California state boundary: https://data.ca.gov/dataset/
"""

import logging
from pathlib import Path

import geopandas as gpd
from pyproj import CRS
import matplotlib.pyplot as plt
import contextily as cx

from utils.paths import get_input_path, get_output_path


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def load_input_path(filename: str) -> Path:
    """
    Resolve the path to the input GeoPackage file.

    Parameters
    ----------
    filename : str
        Input geospatial file name.

    Returns
    -------
    file_path: Path
        Path to the GeoPackage file containing US National Parks units.
    """
    file_path = get_input_path(filename)
    logger.info("Resolved input path: %s", file_path)
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
    gdf: gpd.GeoDataFrame
        Loaded GeoDataFrame.
    """
    gdf = gpd.read_file(file_path)
    logger.info("GeoDataFrame loaded: %s", file_path)
    return gdf

def clean_gdf(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Validate and clean a GeoDataFrame.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The GeoDataFrame to clean and validate.

    Returns
    -------
    gdf: gpd.GeoDataFrame
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

    target = CRS.from_user_input(target_crs)

    if gdf.crs != target:
        gdf = gdf.to_crs(target)
        logger.info("Reprojected to %s", gdf.crs)
    else:
        logger.info("Projection already in %s" ,gdf.crs)

    return gdf

def prepare_gdf(filename: str, target_crs: str) -> gpd.GeoDataFrame:
    """
    Load, clean, and reproject a geospatial dataset.

    Parameters
    ----------
    filename : str
        Input geospatial file name.
    target_crs : str
        CRS to reproject to.

    Returns
    -------
    gpd.GeoDataFrame
        Processed GeoDataFrame.
    """
    path = load_input_path(filename)
    gdf = load_gdf(path)
    gdf = clean_gdf(gdf)
    gdf = reproject_gdf(gdf, target_crs)
    return gdf

def log_park_summary(gdf: gpd.GeoDataFrame) -> None:
    """
    Log summary statistics and descriptive information for park data.

    This function provides high-level insights into the park dataset,
    including total counts, state-level filtering, and basic aggregation.
    It is intended for exploratory analysis and reporting only and does
    not modify or return the input GeoDataFrame.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        GeoDataFrame containing National Park unit geometries and
        associated attributes.

    Returns
    -------
    None
        This function returns no value and is used for logging and
        exploratory inspection.
    """

    logger.info("Parks total: %s", len(gdf))
    logger.info("Parks in CA: %s", len(gdf.loc[gdf['STATE']=='CA']))
    logger.info("Park names in CA: %s", gdf.loc[gdf['STATE']=='CA', 'PARKNAME'])

    grouped = gdf.dissolve(by='STATE', as_index=False)
    logger.info("There are park units in %s states", len(grouped['STATE']))

    return

def analyze_state_clipped_parks(parks_gdf: gpd.GeoDataFrame, state_gdf: gpd.GeoDataFrame) -> None:
    """
    Clip National Park unit geometries to a state boundary and quantify area loss.

    This function performs a spatial clip operation between National Park
    unit geometries and a single-state boundary. It computes both
    dataset-level and feature-level area statistics to identify parks
    that are partially outside the target state.

    The function logs:
    - Total national park area
    - Total park area within the state
    - Percentage of total park area within the state
    - Feature-level percentage of each park retained after clipping

    Parks whose clipped area differs from their original area are
    identified as crossing the state boundary.

    Parameters
    ----------
    parks_gdf : gpd.GeoDataFrame
        GeoDataFrame containing National Park unit geometries. Must be
        projected in an equal-area CRS.
    state_gdf : gpd.GeoDataFrame
        GeoDataFrame containing a single state boundary geometry,
        projected in the same CRS as `parks_gdf`.

    Returns
    -------
    gpd.GeoDataFrame
        GeoDataFrame of National Park units clipped to the state boundary,
        including only the portions that lie within the state.
    """

    if parks_gdf.crs != state_gdf.crs:
        raise ValueError("parks_gdf and state_gdf must share the same CRS")
    
    if len(state_gdf) != 1:
        raise ValueError("state_gdf must contain exactly one geometry")

    # --- Dataset-level summary ---

    # Calculate total area of all parks (km²) before clipping
    total_parks_area_km2 = round(parks_gdf.area.sum()/1000000,2)
    logger.info("Total national park area: %s km2", total_parks_area_km2)

    # Clip park geometries to the state boundary
    # This identifies portions of parks within the state
    parks_clipped = gpd.clip(parks_gdf, state_gdf)
    logger.info("Clipped parks in CA: %s", parks_clipped.loc[parks_clipped['STATE']=='CA', 'PARKNAME'])

    # Calculate total area after clipping
    clipped_parks_area_km2 = round(parks_clipped.area.sum()/1000000,2)
    logger.info("California parks area: %s km2", clipped_parks_area_km2)

    # Compute the percentage of park area retained within the state
    clipped_area_percentage = round(clipped_parks_area_km2 / total_parks_area_km2 * 100,2)
    logger.info("California area percentage: %s", clipped_area_percentage)


    # --- Feature-level comparison ---

    # Copy original parks to preserve data before adding area columns
    parks_copy = parks_gdf.copy()
    parks_copy['area_original_gdf'] = parks_copy.area
    parks_clipped['area_clipped_gdf'] = parks_clipped.area

    # Merge clipped parks with original areas to compare per park
    parks_area_comparison = parks_clipped.merge(parks_copy, how='inner', on='fid')
    
    # Compute percentage of each park's area that remains after clipping
    parks_area_comparison['area_comparison'] = (parks_area_comparison['area_clipped_gdf'] / parks_area_comparison['area_original_gdf'] * 100).round().astype(int)

    # Log parks that were partially clipped
    if (parks_area_comparison['area_comparison'] != 100).any():
        logger.info("NP area %s was clipped by the California state boundary", parks_area_comparison.loc[parks_area_comparison['area_comparison']!=100, 'fid'])
    else:
        logger.info("No NP were clipped by the California state boundary")

    return parks_clipped, state_gdf

def plot_park_areas_by_state(parks_clipped: gpd.GeoDataFrame, state_gdf: gpd.GeoDataFrame) -> None:
    """
    Plot clipped National Park areas within state boundary.

    This function visualizes National Park unit geometries that have been
    clipped to state boundary. Park polygons are symbolized by their
    clipped area values, and the state boundary is shown as an outline.
    A web basemap is added for geographic context.

    All geometries are reprojected to Web Mercator (EPSG:3857) for
    compatibility with the basemap.

    Parameters
    ----------
    parks_clipped : gpd.GeoDataFrame
        GeoDataFrame of National Park units clipped to a state boundary.
        Must include an 'area_clipped_gdf' column.
    state_gdf : gpd.GeoDataFrame
        GeoDataFrame containing the corresponding state boundary geometry.

    Returns
    -------
    None
        Displays a map of clipped park areas.
    """

    parks_wm = parks_clipped.to_crs(epsg=3857)
    state_wm = state_gdf.to_crs(epsg=3857)

    parks_wm['area_clipped_gdf'] = parks_wm['area_clipped_gdf'].round(2)
    
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)

    state_wm.plot(ax=ax,
                  color='none',
                  edgecolor='black',
                  linewidth=0.8,
                  zorder=1)

    parks_wm.plot(ax=ax,
                  column="area_clipped_gdf",
                  cmap="viridis",
                  legend=True,
                  legend_kwds={"label": "Park area (km²)"})

    cx.add_basemap(ax, source=cx.providers.CartoDB.PositronNoLabels)

    ax.set_title("National Park Areas Within State Boundary", fontsize=12)
    ax.set_axis_off()
    plt.show();

    return

if __name__ == "__main__":

    target_crs = 'EPSG:5070'

    parks_gdf = prepare_gdf("us_nps_units_parks.gpkg", target_crs)
    state_gdf = prepare_gdf("california_state_boundary.gpkg", target_crs)

    log_park_summary(parks_gdf)
    parks_clipped, state_gdf = analyze_state_clipped_parks(parks_gdf, state_gdf)

    plot_park_areas_by_state(parks_clipped, state_gdf)

# Finetune plot
# Save to drive, add to github
# Test interactive map: https://geopandas.org/en/stable/docs/user_guide/interactive_mapping.html
