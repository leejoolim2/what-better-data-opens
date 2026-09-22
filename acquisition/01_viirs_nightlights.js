/* Google Earth Engine — VIIRS monthly nightlights aggregated to ADM2
 * Chapters 3, 6, 7, 12, 14 use this schema.
 * Run at https://code.earthengine.google.com  (free account, browser only)
 * Output columns match data/ch03_viirs_panel_adm2.csv exactly.
 */
var CITY_ISO = 'KHM';                      // KHM VNM UZB KEN USA GBR
var START = '2019-01-01', END = '2024-12-31';

var adm2 = ee.FeatureCollection('projects/sat-io/open-datasets/geoboundaries/CGAZ_ADM2')
             .filter(ee.Filter.eq('shapeGroup', CITY_ISO));

var viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
              .filterDate(START, END);

var rows = viirs.map(function (img) {
  var stats = img.select(['avg_rad', 'cf_cvg']).reduceRegions({
    collection: adm2,
    reducer: ee.Reducer.mean(),
    scale: 500
  });
  var d = img.date().format('YYYY-MM-01');
  return stats.map(function (f) {
    return f.set('date', d).set('shapeGroup', CITY_ISO);
  });
}).flatten();

Export.table.toDrive({
  collection: rows,
  description: 'viirs_' + CITY_ISO,
  fileFormat: 'CSV',
  selectors: ['shapeID', 'shapeName', 'shapeGroup', 'date', 'avg_rad', 'cf_cvg']
});
/* NOTE. cf_cvg is the count of cloud-free observations. Rows with cf_cvg = 0
 * carry no usable radiance; drop them rather than treating avg_rad as zero.
 * This is why the synthetic file also contains missing values. */
