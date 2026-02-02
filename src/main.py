import logging
from dataclasses import dataclass
import geopandas as gpd
from pyproj import CRS
import numpy as np

import geopandas_demo
import requests_demo

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
    target_crs = 'EPSG:5070'
    parks_filename = "us_nps_units_parks.gpkg"
    state_filename = "california_state_boundary.gpkg"

    return UserInput(
        target_crs = target_crs,
        parks_filename = parks_filename,
        state_filename = state_filename
    )

def run_vector_pipeline(UserInput: UserInput) -> gpd.GeoDataFrame:
    logger.info("Entering geopandas demo")

    parks_gdf = geopandas_demo.prepare_gdf(UserInput.parks_filename, UserInput.target_crs)
    state_gdf = geopandas_demo.prepare_gdf(UserInput.state_filename, UserInput.target_crs)

    geopandas_demo.log_park_summary(parks_gdf)
    parks_clipped, state_gdf = geopandas_demo.analyze_state_clipped_parks(parks_gdf, state_gdf)

    geopandas_demo.plot_park_areas_by_state(parks_clipped, state_gdf)

    return parks_clipped


def prepare_raster_bounding_boxes(parks_clipped: gpd.GeoDataFrame) -> dict:
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

def run_raster_pipeline(parks_dict):
    logger.info("Entering requests demo")

    current_park = parks_dict[0]
    naip_response = requests_demo.download_naip(current_park)
    requests_demo.save_naip_response(current_park, naip_response)

filled_user_input = user_input()
parks_clipped = run_vector_pipeline(filled_user_input)
parks_dict = prepare_raster_bounding_boxes(parks_clipped)
run_raster_pipeline(parks_dict)