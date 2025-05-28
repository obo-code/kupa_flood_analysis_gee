# kupa_flood_analysis_gee
Multi-sensor flood and vegetation impact analysis in the Kupa River basin (Croatia) using Google Earth Engine. Open and replicable workflow for flood detection and environmental impact assessment using GEE and open data and open-source data.

This repository contains the code and description for the remote sensing analysis of the May 2023 flood event in the Kupa River Basin, Croatia. The study combines open-access satellite datasets and free cloud-based tools to detect flood extent and assess its environmental impacts without field access.

🛰️ Datasets Used
Sentinel-1 SAR (VH polarization): For flood detection through backscatter analysis.
Sentinel-2 MSI: Used to calculate NDVI for assessing vegetation stress and flood impact.
CHIRPS Precipitation: Daily and monthly rainfall data used to link flood events to precipitation intensity.

🛠️ Tools and Platform
Google Earth Engine (GEE) – cloud-based geospatial analysis
QGIS – for visualization and cartographic layout
Python (optional) – for further data analysis or visualization

🔁 Reproducibility
All scripts are written in Google Earth Engine JavaScript API and can be run directly via code.earthengine.google.com.
To reproduce the study in your region:

1. Replace the area of interest geometry (geometry) with your desired boundary.
   In this study, the geometry object was created manually using the polygon drawing tool in GEE, representing the Kupa River Basin.
2. Adjust the analysis period and thresholds if needed.


