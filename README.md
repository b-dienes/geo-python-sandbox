# Geo Python Sandbox

A repository for practicing geospatial Python workflows, demonstrating proficiency in multiple Python GIS libraries.  
It contains modular, reproducible code for common vector and raster operations, spatial analysis, and geospatial data processing.  

The project is structured to support exploration of multiple geospatial Python libraries, including GeoPandas and Rasterio, with a focus on clear, maintainable, and professional code.

---

## Technology Stack

Core geospatial Python libraries demonstrated in this repository:

- **GeoPandas** – vector data manipulation, spatial operations, reprojection
- **PyProj** – coordinate reference system handling
- **Rasterio** – raster data processing (placeholder for future exercises)
- **Shapely** – geometry operations
- **Matplotlib / Folium** – for future visualizations

---

## **Architecture / Project Structure**

```text
geo-python-sandbox/
├── data/
│   ├── inputs/       # Place input datasets here (GeoPackage, shapefiles, raster files)
│   └── outputs/      # Outputs from scripts (processed GeoDataFrames, exports, plots)
├── src/
│   ├── geopandas_demo.py       # GeoPandas workflow: vector processing, clipping, area analysis
│   ├── main.py                 # Pipeline linking vector processing and raster preparation
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

> Note: The National Parks dataset used is a filtered subset to simplify analysis and reduce runtime.

### Results
- Console logging provides dataset-level insights:
  - Total national park area
  - California parks area
  - Percentage of total area retained within the state
  - Park units partially clipped by the California boundary

- Planned visualizations:
  - Maps showing park areas before and after clipping

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
- Demonstrate end-to-end vector-to-raster workflows