import logging
from dataclasses import dataclass
import geopandas as gpd
import geopandas_demo
from pyproj import CRS

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
    logger.info("Entering Mercator reprojection")
    target_crs = CRS.from_user_input("EPSG:3857")

    if parks_clipped.crs != target_crs:
        parks_clipped = parks_clipped.to_crs(target_crs)

    parks_clipped['BBOX_MINX'] = parks_clipped.bounds['minx']
    parks_clipped['BBOX_MINY'] = parks_clipped.bounds['miny']
    parks_clipped['BBOX_MAXX'] = parks_clipped.bounds['maxx']
    parks_clipped['BBOX_MAXY'] = parks_clipped.bounds['maxy']
    parks_reduced = parks_clipped[['fid', 'PARKNAME', 'BBOX_MINX', 'BBOX_MINY', 'BBOX_MAXX', 'BBOX_MAXY']]

    parks_dict = parks_reduced.to_dict('list')

    logger.info("Parks dict: %s", parks_dict)

    return parks_dict

filled_user_input = user_input()
parks_clipped = run_vector_pipeline(filled_user_input)
parks_dict = prepare_raster_bounding_boxes(parks_clipped)
