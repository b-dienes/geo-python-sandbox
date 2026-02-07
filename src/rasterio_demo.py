import rasterio

from pathlib import Path
from utils.paths import get_input_path, get_output_path


def prepare_raster(naip_image_path: Path) -> None:


    dataset = rasterio.open(naip_image_path)

    print(dataset.meta)

    array = dataset.read(1)


    # TODO:
    # Save CRS with NAIP response (see dataset.meta)
	# Compute a simple band statistic (NDVI, mean brightness, histogram).
	# Mask raster using your clipped parks polygons (vector → raster mask).

    return array

def save_raster(naip_image_array, naip_image_band1_path):

    with rasterio.open(
        naip_image_band1_path,
        'w',
        driver='GTiff',
        height=naip_image_array.shape[0],
        width=naip_image_array.shape[1],
        count=1,
        dtype=naip_image_array.dtype,
        crs=naip_image_array.crs,
        transform=naip_image_array.transform,
    ) as dst:
        dst.write(naip_image_array, 1)

if __name__ == "__main__":
    naip_image_path = get_output_path("Sequoia.tif")
    naip_image_band1_path = get_output_path("Sequoia_band1.tif")
    naip_image_array = prepare_raster(naip_image_path)
    save_raster(naip_image_array, naip_image_band1_path)