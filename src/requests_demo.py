"""
Satellite imagery downloader for NAIP datasets.

This module provides functions to request and save NAIP raster imagery
for specified park bounding boxes. Images are retrieved in TIFF format
from the USGS ImageServer and stored locally in the outputs folder.
"""

import logging
import requests
from dataclasses import dataclass
from utils.inputs import UserInput


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

@dataclass
class NAIPImage:
    park_name: str
    tile_code: str
    data: bytes
    width: int
    height: int
    crs: int
    bbox: list

def download_naip(current_tile: dict, user_input: UserInput) -> NAIPImage:
    """
    Send a request to the NAIP ImageServer to download imagery for the specified bounding box.

    Parameters
    ----------
    current_tile : dict
        Current park bounding box prepared for raster download.

    Returns
    -------
    response.content : bytes
        Raw binary content of the downloaded NAIP image (TIFF format).

    Raises
    -------
    requests.exceptions.Timeout
        If the server does not respond within the timeout.
    requests.exceptions.RequestException
        For other network-related errors.
    ValueError
        If the downloaded content is empty.
    """

    logger.info("Entered NAIP download with %s", current_tile["parkname"])

    park_name = current_tile["parkname"]
    tile_code = current_tile["tile_code"]
    width = user_input.naip_width
    height = user_input.naip_height
    bbox_list = current_tile["tile_bbox"]
    bbox_str = ','.join(map(str, bbox_list))
    crs =  102100

    url = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer/exportImage"
    params = {
    "bbox": bbox_str,
    "bboxSR": crs,
    "imageSR": crs,
    "size": str(width) + ',' + str(height),
    "adjustAspectRatio": True,
    "format": "tiff",
    "f": "image",
    "dpi":96}

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("NAIP download timed out. Check internet connection or AOI size")
        raise
    except requests.exceptions.RequestException as e:
        logger.error(f"NAIP download failed due to network error: {e}")
        raise
    if not response.content:
        raise ValueError("NAIP download content is empty, Check your AOI")
    
    data = response.content

    return NAIPImage(
        park_name = park_name,
        tile_code = tile_code,
        data = data,
        width = width,
        height = height,
        crs = crs,
        bbox = bbox_list
    )