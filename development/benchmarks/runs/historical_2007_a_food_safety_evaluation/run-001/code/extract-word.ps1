$ErrorActionPreference = 'Stop'
$runDir = Split-Path -Parent $PSScriptRoot
$sourceFile = Get-ChildItem -LiteralPath (Join-Path $runDir 'source-provenance/original') -Filter '*.doc' | Select-Object -First 1
$extractionDir = Join-Path $runDir 'extraction'
New-Item -ItemType Directory -Force -Path $extractionDir | Out-Null
$output = Join-Path $extractionDir 'word-com-result.json'
$word = $null
$doc = $null
$result = @{
    extractor = 'Microsoft Word COM, read-only, macros disabled'
    status = 'UNVERIFIED'
    source = $sourceFile.FullName
}
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $doc = $word.Documents.Open($sourceFile.FullName, $false, $true, $false)
    $bodyPath = Join-Path $runDir 'extraction/word-com-text.txt'
    $bodyText = (($doc.Content.Text -replace "`r`n", "`n" -replace "`r", "`n").TrimEnd([char[]]"`n")) + "`n"
    [System.IO.File]::WriteAllText($bodyPath, $bodyText, [System.Text.UTF8Encoding]::new($false))
    $tables = @()
    foreach ($table in $doc.Tables) {
        $cells = @()
        foreach ($cell in $table.Range.Cells) {
            $cells += @{ row=$cell.RowIndex; column=$cell.ColumnIndex; text=$cell.Range.Text }
        }
        $tables += @{ rows=$table.Rows.Count; columns=$table.Columns.Count; cells=$cells }
    }
    $result.status = 'PASS'
    $result.version = $word.Version
    $result.pages = $doc.ComputeStatistics(2)
    $result.table_count = $doc.Tables.Count
    $result.inline_shape_count = $doc.InlineShapes.Count
    $result.shape_count = $doc.Shapes.Count
    $result.field_count = $doc.Fields.Count
    $result.tables = $tables
    $doc.ExportAsFixedFormat((Join-Path $runDir 'extraction/word-com-render.pdf'), 17)
} catch {
    $result.status = 'FAILED'
    $result.error_type = $_.Exception.GetType().FullName
    $result.error = $_.Exception.Message
} finally {
    if ($null -ne $doc) { $doc.Close(0) }
    if ($null -ne $word) { $word.Quit() }
    $resultJson = ($result | ConvertTo-Json -Depth 8) -replace "`r`n", "`n"
    [System.IO.File]::WriteAllText($output, $resultJson + "`n", [System.Text.UTF8Encoding]::new($false))
}
