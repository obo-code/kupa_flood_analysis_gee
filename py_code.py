// 1. ROI
var kupa = geometry;
Map.centerObject(kupa, 12);

// 2. DATES – before and after
var beforeStart = '2023-05-01';
var beforeEnd = '2023-05-15';
var afterStart = '2023-05-16';
var afterEnd = '2023-05-19';

// 3. SENTINEL-1 SAR 
var s1collection = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(kupa)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'));

// CHeck up
print('Before image count:', s1collection.filterDate(beforeStart, beforeEnd).size());
print('After image count:', s1collection.filterDate(afterStart, afterEnd).size());

// 4. Median image – before and after
var before = s1collection
  .filterDate(beforeStart, beforeEnd)
  .select('VH')
  .median();

var after = s1collection
  .filterDate(afterStart, afterEnd)
  .select('VH')
  .median();

// 7. BACKSCATTER difference
var diff = before.subtract(after);

// 8. flood mask
var floodChange = diff.gt(1.0); // 

// Korak 3: additional maks for AFTER < choose treshold
var floodMask = floodChange.and(after.lt(-15));

//  mapping
Map.addLayer(before.clip(kupa), {min: -25, max: -5, palette: ['white', 'black']}, 'Before VH dB');
Map.addLayer(after.clip(kupa), {min: -25, max: -5, palette: ['white', 'black']}, 'After VH dB');
Map.addLayer(floodMask.updateMask(floodMask).clip(kupa),{palette: ['blue']},'Flooded areas (change detection)');


var sarViz = {
  min: -25,
  max: -5,
  palette: ['blue', 'white', 'brown']
};

Map.addLayer(before.clip(kupa), sarViz, 'VH dB Color BEFORE');

var sarViz = {
  min: -25,
  max: -5,
  palette: ['blue', 'white', 'brown']
};

Map.addLayer(after.clip(kupa), sarViz, 'VH dB Color AFTER');

// 2. S2 DATES – before and after
var beforeStart = '2023-05-01';
var beforeEnd = '2023-05-15';
var afterStart = '2023-05-16';
var afterEnd = '2023-05-23';

// Sentinel-2 
var S2 = ee.ImageCollection('COPERNICUS/S2')
  .filterBounds(kupa)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) // isključi slike s previše oblaka
  
// Sentinel-2 
var beforeNDVI = S2.filterDate(beforeStart, beforeEnd).map(function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);  // Dodaj NDVI bandu
}).median();

var afterNDVI = S2.filterDate(afterStart, afterEnd).map(function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);  // Dodaj NDVI bandu
}).median();

// check up
print('Before NDVI bands:', beforeNDVI.bandNames());
print('After NDVI bands:', afterNDVI.bandNames());

// bands exsistance
if (beforeNDVI.bandNames().contains('NDVI') && afterNDVI.bandNames().contains('NDVI')) {
  // Izračunaj razliku između NDVI prije i nakon poplave
  var ndviDiff = beforeNDVI.select('NDVI').subtract(afterNDVI.select('NDVI'));
  
  // Mapping NDVI diff
  Map.addLayer(ndviDiff.clip(kupa), {min: -0.5, max: 0.5, palette: ['red', 'white', 'green']}, 'NDVI Difference');
} else {
  print('NDVI bands are missing from one or both images!');
}

// export image
Export.image.toDrive({
  image: ndviDiff.clip(kupa),
  description: 'NDVI_Difference_Export_EPSG3765',
  scale: 10,  
  region: kupa,
  fileFormat: 'GeoTIFF',
  maxPixels: 1e9,
  crs: 'EPSG:3765'  
});

// Refine flood mask (SAR)
var floodMaskSAR = floodMask.updateMask(floodMask);

// Refine NDVI difference mask (NDVI vegetation loss)
var floodMaskNDVI = ndviDiff.lt(-0.10); // NDVI threshold for vegetation damage

var combinedFloodMaskAND = floodMaskSAR.and(floodMaskNDVI);
var combinedFloodMaskOR = floodMaskSAR.or(floodMaskNDVI);

// Display the combined masks on the map
// Map.addLayer(combinedFloodMaskAND.updateMask(combinedFloodMaskAND).clip(kupa), {palette: ['blue']}, 'Flood + Vegetation Damage (AND)');
Map.addLayer(combinedFloodMaskOR.updateMask(combinedFloodMaskOR).clip(kupa), {palette: ['red', 'yellow']}, 'Flood or Vegetation Damage (OR)');

Export.image.toDrive({
  image: combinedFloodMaskOR.clip(kupa),
  description: 'combinedFloodMaskOR',
  scale: 10,  
  region: kupa,
  fileFormat: 'GeoTIFF',
  maxPixels: 1e9,
  crs: 'EPSG:3765'  
});

// Load Sentinel-3 OLCI data 
var s3 = ee.ImageCollection('COPERNICUS/S3/OLCI')
  .filterBounds(kupa)
  .filterDate(beforeStart, afterEnd)
  .select(['Oa04_radiance', 'Oa05_radiance', 'Oa06_radiance', 'Oa08_radiance']);  // Red, Green, Blue, and NIR bands

// Compute NDVI from Sentinel-3 OLCI (using Red and NIR bands)
var s3NDVI = s3.map(function(image) {
  var ndvi = image.normalizedDifference(['Oa08_radiance', 'Oa04_radiance']).rename('NDVI');  // NIR and Red bands
  return image.addBands(ndvi);
});

// Compute the median NDVI for the time period before and after the flood
var beforeS3NDVI = s3NDVI.filterDate(beforeStart, beforeEnd).median().select('NDVI');
var afterS3NDVI = s3NDVI.filterDate(afterStart, afterEnd).median().select('NDVI');

// Calculate the NDVI difference (change in vegetation)
var ndviDiffS3 = beforeS3NDVI.subtract(afterS3NDVI);

// Improved visualization of NDVI Difference (vegetation change)
Map.addLayer(ndviDiffS3.clip(kupa), {
  min: -0.4,
  max: 0.4,
  palette: ['red', 'white', 'green'],
  opacity: 0.7
}, 'Sentinel-3 NDVI Difference');

