export const RESEARCH_ID = /^[0-9a-f]{64}$/;
export function safeHistoryPayload(payload) {
  if (!payload || !Array.isArray(payload.records) || !Number.isInteger(payload.total) || payload.total < 0) throw new Error('Invalid research history response');
  return payload.records.filter(record => RESEARCH_ID.test(record.research_id) && typeof record.product_id === 'string' && typeof record.regions === 'string');
}
export function researchReportPath(researchId) {
  if (!RESEARCH_ID.test(researchId)) throw new Error('Invalid research identifier');
  return `/api/research/${researchId}/report.pdf`;
}
export function hasPublishedResearchError(status) {
  return status === 503;
}
