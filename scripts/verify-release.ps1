# Run in a SECOND PowerShell window while start-research-api.ps1 is running.
param([string]$Api = 'http://127.0.0.1:8000', [int]$MinimumResearchRecords = 2)
$ErrorActionPreference = 'Stop'
function Check([string]$name, [string]$url) {
  try { return Invoke-RestMethod -Uri $url -TimeoutSec 20 -ErrorAction Stop }
  catch { throw "$name FAILED at $url. Start the backend first. Details: $($_.Exception.Message)" }
}
$health = Check 'Health' "$Api/api/health"
$status = Check 'Research status' "$Api/api/research/status"
$history = Check 'Research history' "$Api/api/research/history?limit=10"
$regions = Check 'Research regions' "$Api/api/research/available-regions"
if ($status.state -ne 'ready') { throw "Research publication state is '$($status.state)', expected ready." }
if ([int]$status.record_count -lt $MinimumResearchRecords) { throw "Research status reports $($status.record_count) record(s); expected at least $MinimumResearchRecords." }
if ([int]$history.total -lt $MinimumResearchRecords) { throw "Research history contains only $($history.total) record(s)." }
$products = @($history.records | ForEach-Object { $_.product_id })
foreach ($needed in @('gpm_3imergm_07_final','gldas_noah025_m_2_1_soil0_10')) {
  if ($needed -notin $products) { throw "Research history is missing product: $needed" }
}
Write-Host 'PASS: API healthy; research publication ready; both actual IMERG and GLDAS records listed.'
Write-Host "Records: $($status.record_count)"
Write-Host "Products: $($products -join ', ')"
Write-Host 'Country/region evidence response available.'
