// The browser can only select a registered product and a constrained study geometry.
// Never pass a visitor-provided local path or NASA URL to the extraction API.
export function prepareGridRequest(productId, mode, code, bounds) {
  if (!/^[a-z][a-z0-9_]{4,70}$/.test(String(productId || ''))) throw Error('Select an approved product.');
  if (mode === 'country') {
    if (!/^[A-Z]{3}$/.test(String(code || ''))) throw Error('Select a three-letter country code.');
    return { product_id: productId, country_code: code };
  }
  if (mode !== 'rectangle' || !Array.isArray(bounds) || bounds.length !== 4 || bounds.some(v => typeof v !== 'number' || !Number.isFinite(v))) throw Error('Enter four finite rectangle coordinates.');
  const [west, south, east, north] = bounds;
  if (!(west >= -180 && east <= 180 && south >= -90 && north <= 90 && west < east && south < north && east - west <= 25 && north - south <= 25)) throw Error('Rectangle must be WGS84 and at most 25° wide and tall.');
  return { product_id: productId, bbox: bounds };
}
export function gridResultToDashboard(result) {
  if (!result || result.data_status !== 'computed_from_operator_approved_local_grids' || !Array.isArray(result.observations)) throw Error('Invalid scientific extraction response.');
  const units = result.metadata?.normalized_unit || result.metadata?.unit || 'product-normalized unit';
  const variables = {T2M:'temperature', precipitation:'rainfall', SoilMoi0_10cm_inst:'soil_moisture'};
  const variable = variables[result.metadata?.variable_id] || result.product_id;
  return {
    dataset: { metadata: { id: result.research_id, region: result.region_name, variable, product: result.product_id,
      normalized_unit: units, observation_count: result.observation_count, first_month: result.observations[0]?.date, last_month: result.observations.at(-1)?.date,
      source_url: '', verification_status: 'operator_approved_local_grids', coverage_warning: 'Verified only against the approved subset and its documented grid coverage. Product origin is not independently authenticated.' }, observations: result.observations },
    trend: result.trend
  };
}
