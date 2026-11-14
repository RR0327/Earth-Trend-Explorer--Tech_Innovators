export function productStatus(product) {
  if (!product || typeof product !== 'object') return 'Unknown';
  if (product.available_curated_series > 0) return 'Curated series available';
  if (product.integration === 'visitor_csv_only') return 'NASA export required';
  return 'Not available';
}

export function coverageVerdict(preview) {
  if (!preview) return 'No source data previewed';
  if (!preview.requested_region_matches_source) return 'Selected region does not match the source-covered region';
  if (!preview.analysis_available) return 'Insufficient complete years for trend analysis';
  return `${preview.observation_count} observed months · ${preview.complete_years.length} complete years`;
}
