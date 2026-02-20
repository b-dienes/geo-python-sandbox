# Geo Python Sandbox

A repository demonstrating geospatial Python workflows with a focus on vector and raster data processing. 
It contains modular, reproducible code for vector analysis, satellite imagery download , and raster processing with NDVI calculation.
Pipeline orchestration with Airflow/DAGs is planned as a next step.

---

## Technology Stack

Core geospatial Python libraries demonstrated in this repository:

- **GeoPandas** – vector data manipulation, spatial operations, reprojection
- **PyProj** – coordinate reference system handling
- **Matplotlib / Contextily** – geospatial visualization with basemaps
- **Requests** – fetching remote raster datasets
- **Rasterio** – planned for future raster data processing and analysis

---

## **Architecture / Project Structure**

```text
geo-python-sandbox/
├── data/
│   ├── inputs/       # Place input datasets here (GeoPackage, shapefiles, raster files)
│   └── outputs/      # Outputs from scripts (processed GeoDataFrames, exports, plots, downloaded rasters)
├── src/
│   ├── geopandas_demo.py       # GeoPandas workflow: vector processing, clipping, area analysis
│   ├── requests_demo.py        # Satellite imagery download
│   ├── rasterio_demo.py        # Raster workflow: saving NAIP images, loading, NDVI calculation, exporting rasters
│   ├── main.py                 # Pipeline orchestration linking vector and raster processing
│   └── utils/
│       ├── geometry.py         # Tiling based on park polygons and user input
│       ├── inputs.py           # User input handling
│       └── paths.py            # Helper functions for resolving file paths
├── README.md
└── .gitignore
```

---

## GeoPandas: Vector Data Processing

### Workflow
This module demonstrates professional use of GeoPandas for vector data:

- Load, clean, and validate geospatial datasets
- Reproject to a consistent equal-area CRS
- Log descriptive statistics (total areas, counts, state-level summaries)
- Clip National Park units to California state boundaries
- Compute area differences to identify parks partially outside the state

### Results
- Console logging provides dataset-level insights:
  - Total national park area
  - California parks area
  - Percentage of total area retained within the state
  - Park units partially clipped by the California boundary

- Visualization:
  - Choropleth map of units clipped to the state boundary, color-coded by clipped area

---

## Requests: NAIP Imagery Download

### Workflow
- Prepare bounding boxes / tiles for clipped park polygons based on user input (reprojected to Web Mercator)
- Fetch NAIP aerial imagery via USGS ArcGIS REST API for each tile

### Results
- Downloaded NAIP imagery for sample parks, split into tiles according to user-defined parameters

---

## Rasterio: Raster Data Processing

### Workflow
- Save downloaded NAIP imagery as GeoTIFF files to outputs directory
- Open satellite imagery, calculate NDVI, and save NDVI rasters
- Placeholder for future exercises: clipping NDVI rasters to park polygons, raster/vector overlays

### Results
- Saved GeoTIFFs and NDVI rasters are ready for integration with vector workflows
- Planned outputs:
  - Raster/vector overlays and visualizations

---

## Airflow: Orchestrating Vector and Raster Workflows

### Workflow
- Coordinate end-to-end geospatial processing
- Currently implemented as a sequential Python script (main.py)

### Planned enhancement:
Transition to DAG-style orchestration with Airflow, enabling:
- Parallel download of NAIP imagery per tile
- Independent raster processing tasks per tile
- Future vector-raster overlay tasks for integrated spatial analysis

### Conceptual DAG:
```text
Vector Processing 
       └─> Tile Generation 
               └─> Download NAIP Imagery (per tile, parallel)
                       └─> Raster Processing / NDVI (per tile, parallel)
                               └─> Vector-Raster Overlay (future)
```
