"""
Satellite imagery downloader for NAIP datasets.

This module provides functions to request and save NAIP raster imagery
for specified park bounding boxes. Images are retrieved in TIFF format
from the USGS ImageServer and stored locally in the outputs folder.
"""


import logging
import requests
from pathlib import Path
from utils.paths import get_input_path, get_output_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def download_naip(current_park: dict) -> bytes:
    """
    Send a request to the NAIP ImageServer to download imagery for the specified bounding box.

    Parameters
    ----------
    current_park : dict
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

    logger.info("Entered NAIP download with %s", current_park["parkname"])

    xmin = current_park["bbox"][0]
    ymin = current_park["bbox"][1]
    xmax = current_park["bbox"][2]
    ymax = current_park["bbox"][3]

    url = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPImagery/ImageServer/exportImage"
    params = {
    "bbox": str(xmin) + ',' + str(ymin) + ',' + str(xmax) + ',' + str(ymax),
    "bboxSR": 102100,
    "imageSR": 102100,
    "size": str(2500) + ',' + str(2500),
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
        
    return response.content

def save_naip_response(current_park: dict, naip_response: bytes) -> Path:
    """
    Save the downloaded NAIP image to the outputs folder.

    Parameters
    ----------
    current_park : dict
        Current park bounding box prepared for raster download.

    naip_response : bytes
        Raw binary content of the downloaded NAIP image (TIFF format).
    
    Returns
    -------
    None
        Saves NAIP imagery to the outputs folder.

    Raises
    -------
        PermissionError
            If the output file cannot be written due to insufficient permissions.
    """

    aoi_name = current_park["parkname"]
    filename = f"{aoi_name}.tif"

    output_path = get_output_path(filename)

    try:
        with open(output_path, 'wb') as f:
                f.write(naip_response)
    except PermissionError:
        logger.error("No permission to write NAIP image to %s", output_path)
        raise

    logger.info("NAIP image saved to %s", output_path)

    return output_path