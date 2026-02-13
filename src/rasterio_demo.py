"""
Save NAIP tiles locally, compute NDVI, and export NDVI rasters with safe filenames.
"""

import logging
import re
from pathlib import Path

import rasterio
import numpy as np

from utils.paths import get_input_path, get_output_path
from requests_demo import NAIPImage


logger = logging.getLogger(__name__)

def slugify(text: str) -> str:
    """
    Convert a string into a filesystem-safe slug.
    
    Replaces non-alphanumeric characters with '_', strips
    leading/trailing underscores, and converts to lowercase.
    
    Parameters
    ----------
    text : str
        Input string to slugify.
        
    Returns
    -------
    str
        Filesystem-safe string.
    """
    text = re.sub(r'[^A-Za-z0-9_-]+', '_', text)
    return text.strip('_').lower()


def make_naip_filename(naip_response: NAIPImage, suffix: str = "") -> str:
    """
    Generate a safe filename for a NAIP tile.
    
    Parameters
    ----------
    naip_response : NAIPImage
        Dataclass containing metadata for 'park_name' and 'tile_code'.
    suffix : str, optional
        Optional suffix before the extension (e.g., "_ndvi").
    
    Returns
    -------
    str
        Filename like "devils_postpile_-5303_1809_ndvi.tif"
    """
    aoi_name = naip_response.park_name
    tile_code = naip_response.tile_code

    base = f"{slugify(aoi_name)}_{tile_code}"
    filename = f"{base}{suffix}.tif"

    return filename


def save_naip_response(naip_response: NAIPImage) -> Path:
    """
    Save raw NAIP imagery to the outputs folder.
    
    Parameters
    ----------
    naip_response : NAIPImage
        Dataclass with tile metadata and raw binary image data.
    
    Returns
    -------
    Path
        Path to the saved .tif file.
    
    Raises
    ------
    PermissionError
        If the output cannot be written.
    """
    filename = make_naip_filename(naip_response)
    output_path = get_output_path(filename)

    try:
        with open(output_path, 'wb') as f:
                f.write(naip_response.data)
    except PermissionError:
        logger.error("No permission to write NAIP image to %s", output_path)
        raise

    logger.info("NAIP image saved to %s", output_path)

    return output_path


def calculate_ndvi(naip_image_path: Path) -> tuple[rasterio.io.DatasetReader, np.ndarray]:
    """
    Compute NDVI from a NAIP image.
    
    Uses NIR (band 4) and Red (band 1). Adds a small epsilon
    to denominator to avoid division by zero.
    
    Parameters
    ----------
    naip_image_path : Path
        Path to the NAIP .tif image.
    
    Returns
    -------
    tuple[rasterio.io.DatasetReader, np.ndarray]
        Opened dataset and NDVI array (float32).
    """
    logger.info("Calculating NDVI for %s", naip_image_path)

    with rasterio.open(naip_image_path) as dataset:

        red = dataset.read(1).astype(np.float32)
        nir = dataset.read(4).astype(np.float32)

        ndvi = (nir - red) / (nir + red + 1e-6)

    return dataset, ndvi


def save_ndvi_raster(naip_dataset: rasterio.io.DatasetReader, naip_image_array: np.ndarray, naip_response: NAIPImage):
    """
    Save NDVI array to a GeoTIFF file.
    
    Parameters
    ----------
    naip_dataset : rasterio.io.DatasetReader
        Original NAIP dataset (for CRS and transform).
    naip_image_array : np.ndarray
        NDVI array to save.
    naip_response : NAIPImage
        Dataclass with tile metadata (used for filename).
    
    Returns
    -------
    Path
        Path to the saved NDVI raster.
    """
    filename = make_naip_filename(naip_response, "_ndvi")
    output_path = get_output_path(filename)

    with rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=naip_image_array.shape[0],
        width=naip_image_array.shape[1],
        count=1,
        dtype=naip_image_array.dtype,
        crs=naip_dataset.crs,
        transform=naip_dataset.transform,
    ) as dst:
        dst.write(naip_image_array, 1)

    logger.info("NDVI raster saved for %s", output_path)
