"""
Download NAIP imagery for park tiles and return satelite imagery and tile data as NAIPImage objects.
"""

import logging

import requests

from dataclasses import dataclass
from utils.inputs import UserInput


logger = logging.getLogger(__name__)

@dataclass
class NAIPImage:
    park_name: str
    tile_code: str
    data: bytes
    width: int
    height: int
    crs: int
    bbox: list[float]

def download_naip(current_tile: dict, user_input: UserInput) -> NAIPImage:
    """
    Download a NAIP image tile from the USGS ImageServer.

    Parameters
    ----------
    current_tile : dict
        Dictionary containing tile metadata:
        - 'fid': str
        - 'parkname': str
        - 'tile_code': str
        - 'tile_bbox': list of floats [xmin, ymin, xmax, ymax]
    user_input : UserInput
        Dataclass containing user-defined download parameters, e.g., image width and height.

    Returns
    -------
    naip_response: NAIPImage
        Dataclass containing raw TIFF bytes and metadata for the tile.

    Raises
    ------
    requests.exceptions.Timeout
        If the server does not respond within the timeout period.
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
