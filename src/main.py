"""
Main module for geospatial workflows.

This script orchestrates vector and raster workflows:
- Loads, cleans, and reprojects GeoDataFrames
- Clips NPS units to a state boundary
- Logs descriptive statistics
- Prepares bounding boxes for raster download
- Downloads NAIP imagery for sample parks
"""

import logging
from dataclasses import dataclass
import geopandas as gpd
from pyproj import CRS

import geopandas_demo
import requests_demo
from requests_demo import NAIPImage
import rasterio_demo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class UserInput:
    target_crs: str
    parks_filename: str
    state_filename: str

def user_input() -> UserInput:
    """
    Prepare default user inputs for the geospatial workflow.

    Returns
    -------
    UserInput
        Dataclass containing CRS, parks filename, and state filename.
    """
    target_crs = 'EPSG:5070'
    parks_filename = "us_nps_units_parks.gpkg"
    state_filename = "california_state_boundary.gpkg"

    return UserInput(
        target_crs = target_crs,
        parks_filename = parks_filename,
        state_filename = state_filename
    )

def run_vector_pipeline(user_input: UserInput) -> gpd.GeoDataFrame:
    """
    Run the vector workflow: load, clean, reproject, log stats, clip parks to state.

    Parameters
    ----------
    user_input : UserInput
        User-defined parameters for CRS and input filenames.

    Returns
    -------
    gpd.GeoDataFrame
        parks_clipped: GeoDataFrame of parks clipped to the state.
    """
    logger.info("Entering geopandas demo")

    parks_gdf = geopandas_demo.prepare_gdf(user_input.parks_filename, user_input.target_crs)
    state_gdf = geopandas_demo.prepare_gdf(user_input.state_filename, user_input.target_crs)

    geopandas_demo.log_park_summary(parks_gdf)
    parks_clipped, state_gdf = geopandas_demo.analyze_state_clipped_parks(parks_gdf, state_gdf)

    geopandas_demo.plot_park_areas_by_state(parks_clipped, state_gdf)

    return parks_clipped


def prepare_raster_bounding_boxes(parks_clipped: gpd.GeoDataFrame) -> list[dict]:
    """
    Prepare bounding boxes for raster requests in Web Mercator projection.

    Parameters
    ----------
    gpd.GeoDataFrame
        parks_clipped : GeoDataFrame of parks clipped to the state boundary.

    Returns
    -------
    list[dict]
        List of dictionaries with keys: "fid", "parkname", "bbox" for raster download.
    """
    logger.info("Entered bbox reprojection to Mercator")
    target_crs = CRS.from_user_input("EPSG:3857")

    if parks_clipped.crs != target_crs:
        parks_clipped = parks_clipped.to_crs(target_crs)

    bboxes = parks_clipped.geometry.bounds.to_numpy().tolist()

    parks_dict = [
        {"fid": i, "parkname": n, "bbox": b}
        for i, n, b in zip(parks_clipped["fid"], parks_clipped["PARKNAME"], bboxes)
    ]

    return parks_dict

def run_image_downloader(current_park: dict) -> NAIPImage:
    """
    Run the NAIP raster download workflow for the current park in the list.

    Parameters
    ----------
    current_park : dict
        Current park with bounding boxes prepared for raster download.

    Returns
    -------
    NAIPImage
        Dataclass.
    """
    logger.info("Entering requests demo")

    naip_response = requests_demo.download_naip(current_park)

    return naip_response

def run_raster_processing(naip_response: NAIPImage) -> None:
    """
    Save the downloaded NAIP image to the outputs folder.

    Parameters
    ----------
    naip_response : NAIPImage
        Dataclass.

    Returns
    -------
    None
    """

    naip_image_path = rasterio_demo.save_naip_response(naip_response)
    rasterio_demo.calculate_ndvi(naip_image_path)

filled_user_input = user_input()
parks_clipped = run_vector_pipeline(filled_user_input)
parks_dict = prepare_raster_bounding_boxes(parks_clipped)


# For testing purposes the first element of the list of dictionaries is used
# Later on it can be a loop feeding dictionaries one by one to run_image_downloader
current_park = parks_dict[0]


naip_response = run_image_downloader(current_park)
run_raster_processing(naip_response)