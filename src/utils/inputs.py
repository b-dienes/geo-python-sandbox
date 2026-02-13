"""
Prepare default user inputs for the geospatial workflow.
"""

from dataclasses import dataclass

@dataclass
class UserInput:
    target_crs: str
    parks_filename: str
    state_filename: str
    naip_resolution: float
    naip_width: int
    naip_height: int

def user_input() -> UserInput:
    """
    Prepare default user inputs for the geospatial workflow.

    Returns
    -------
    UserInput
        Dataclass containing CRS, parks filename, state filename,
        NAIP satellite image pixel size (in meters), width (in pixels), length (in pixels)
    """
    target_crs = 'EPSG:5070'
    parks_filename = "us_nps_units_parks.gpkg"
    state_filename = "california_state_boundary.gpkg"
    naip_resolution = 1.0
    naip_width = 2500
    naip_height = 2500

    return UserInput(
        target_crs = target_crs,
        parks_filename = parks_filename,
        state_filename = state_filename,
        naip_resolution = naip_resolution,
        naip_width = naip_width,
        naip_height = naip_height
    )
