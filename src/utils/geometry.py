from utils.inputs import UserInput

import math
import geopandas as gpd
from pyproj import CRS
import logging

logger = logging.getLogger(__name__)

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

def create_tiles(parks_dict, user_input: UserInput):
    """
    Tiles are generated per park bounding box.
    This design favors implementation clarity over statewide tile reuse.
    In production systems, a master statewide grid would typically be used to avoid redundant downloads.
    """
    # Global origin
    origin_x = 0
    origin_y = 0

    # Define grid steps
    resolution = user_input.naip_resolution
    width = user_input.naip_width
    height = user_input.naip_height

    stepx = width * resolution
    stepy= height * resolution


    all_tiles = []

    for park in parks_dict:

        xmin, ymin, xmax, ymax = park["bbox"]

        # Define global grid cell coordinates covering the current park
        tile_x_start = math.floor(xmin / stepx) * stepx
        tile_y_start = math.floor(ymin / stepy) * stepy

        tile_x_end = math.ceil(xmax / stepx) * stepx
        tile_y_end = math.ceil(ymax / stepy) * stepy

        x = tile_x_start
        while x < tile_x_end:

            y = tile_y_start
            while y < tile_y_end:

                tile = {
                    "fid": park["fid"],
                    "parkname": park["parkname"],
                    "tile_code": f"{int((x - origin_x)/stepx)}_{int((y - origin_y)/stepy)}",
                    "tile_bbox": [x, y, x + stepx, y + stepy]
                }
                all_tiles.append(tile)
                y += stepy
            x += stepx

    return all_tiles