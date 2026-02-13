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
import geopandas as gpd

import geopandas_demo
import requests_demo
import rasterio_demo
from requests_demo import NAIPImage
from utils.inputs import UserInput, user_input
from utils.geometry import prepare_raster_bounding_boxes, create_tiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


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



def run_image_downloader(current_tile: dict, user_input: UserInput) -> NAIPImage:
    """
    Run the NAIP raster download workflow for the current park in the list.

    Parameters
    ----------
    current_tile : dict
        Current park with bounding boxes prepared for raster download.

    Returns
    -------
    NAIPImage
        Dataclass.
    """
    logger.info("Entering requests demo")

    naip_response = requests_demo.download_naip(current_tile, user_input)

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
    naip_dataset, naip_image_array = rasterio_demo.calculate_ndvi(naip_image_path)
    rasterio_demo.save_ndvi_raster(naip_dataset, naip_image_array, naip_response)

filled_user_input = user_input()
parks_clipped = run_vector_pipeline(filled_user_input)

parks_dict = prepare_raster_bounding_boxes(parks_clipped)
all_tiles = create_tiles(parks_dict, filled_user_input)

# For testing purposes the current tiles is the whole bbox of the first park
filtered_tiles = [tile for tile in all_tiles if tile['parkname'] == 'Devils Postpile']

for current_tile in filtered_tiles:

    naip_response = run_image_downloader(current_tile, filled_user_input)

    run_raster_processing(naip_response)

