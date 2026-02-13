import logging
import rasterio
from pathlib import Path
from utils.paths import get_input_path, get_output_path
from requests_demo import NAIPImage
import numpy as np
import re


logger = logging.getLogger(__name__)

def slugify(text):
    # replace bad characters with _
    text = re.sub(r'[^A-Za-z0-9_-]+', '_', text)
    # remove any _ at start or end, lowercase
    return text.strip('_').lower()

def save_naip_response(naip_response: NAIPImage) -> Path:
    """
    Save the downloaded NAIP image to the outputs folder.

    Parameters
    ----------
    naip_response : NAIPImage
        Dataclass.
    
    Returns
    -------
    output_path
        Saves NAIP imagery to the outputs folder. Returns path to the output .tif file.

    Raises
    -------
        PermissionError
            If the output file cannot be written due to insufficient permissions.
    """

    aoi_name = naip_response.park_name
    tile_code = naip_response.tile_code
    filename = f"{slugify(aoi_name)}_{tile_code}.tif"

    output_path = get_output_path(filename)

    try:
        with open(output_path, 'wb') as f:
                f.write(naip_response.data)
    except PermissionError:
        logger.error("No permission to write NAIP image to %s", output_path)
        raise

    logger.info("NAIP image saved to %s", output_path)

    return output_path


def calculate_ndvi(naip_image_path: Path) -> None:

    dataset = rasterio.open(naip_image_path)

    red = dataset.read(1)
    nir = dataset.read(4)

    ndvi = (nir - red) / (nir + red)

    return dataset, ndvi


def save_ndvi_raster(naip_dataset, naip_image_array, naip_response):

    aoi_name = naip_response.park_name
    tile_code = naip_response.tile_code
    filename = f"{slugify(aoi_name)}_{tile_code}_ndvi.tif"
    output_path = get_output_path(filename)

    naip_image_array = naip_image_array.astype(np.float32)

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


if __name__ == "__main__":
    naip_image_path = get_output_path("Sequoia.tif")
    naip_image_band1_path = get_output_path("Dev_NDVI.tif")
    naip_dataset, naip_image_array = calculate_ndvi(naip_image_path)
    save_ndvi_raster(naip_dataset, naip_image_array, naip_image_band1_path)
