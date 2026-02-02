import logging
import requests
from pathlib import Path
from utils.paths import get_input_path, get_output_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def download_naip(current_park):
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



def save_naip_response(current_park, naip_response) -> None:
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
