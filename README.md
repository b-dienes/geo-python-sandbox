# Geo Python Sandbox

A repository demonstrating geospatial Python workflows with a focus on vector and raster data processing. 
It contains modular, reproducible code for vector analysis (fully implemented) and satellite imagery download (functional), with planned raster processing exercises.

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
│   ├── requests_demo.py        # Raster workflow: NAIP imagery download and storage
│   ├── main.py                 # Pipeline linking vector and raster processing
│   └── utils/
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
- Prepare bounding boxes for clipped park polygons (reprojected to Web Mercator)
- Fetch NAIP aerial imagery via USGS ArcGIS REST API for a given park polygon
- Save imagery as GeoTIFF files to outputs directory

### Results
- Downloaded NAIP imagery for sample parks
- Saved GeoTIFFs can be used for future raster/vector integration
- CRS and AOI checks ensure correct alignment with vector datasets

---

## Rasterio: Raster Data Processing (upcoming)

### Workflow
- Placeholder for future exercises with raster datasets
- Demonstrate reading, writing, and analyzing raster data
- Integrate raster/vector workflows for spatial analysis
- Showcase coordinate system transformations and resampling

### Results
- Placeholder for raster analysis visualizations
- Planned outputs:
  - Raster plots
  - Raster/vector overlays
  - Summarized raster statistics

---

## Roadmap

Planned enhancements to the repository:

- Add raster analysis workflows with Rasterio
- Generate visualizations for vector and raster data
- Integrate vector/raster workflows for end-to-end spatial analysis