$ErrorActionPreference = 'Stop'
$runDir = Split-Path -Parent $PSScriptRoot
$sourceFile = Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.doc' | Select-Object -First 1
$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    $doc = $word.Documents.Open($sourceFile.FullName, $false, $true, $false)
    $doc.Content.Text | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'body-word.txt') -Encoding utf8
    $tables = @()
    foreach ($table in $doc.Tables) {
        $cells = @()
        foreach ($cell in $table.Range.Cells) {
            $cells += @{ row=$cell.RowIndex; column=$cell.ColumnIndex; text=$cell.Range.Text }
        }
        $tables += @{ rows=$table.Rows.Count; columns=$table.Columns.Count; cells=$cells }
    }
    @{ extractor='Microsoft Word COM, read-only, macros disabled'; version=$word.Version; pages=$doc.ComputeStatistics(2); table_count=$doc.Tables.Count; inline_shape_count=$doc.InlineShapes.Count; shape_count=$doc.Shapes.Count; field_count=$doc.Fields.Count; tables=$tables } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'word-structure.json') -Encoding utf8
    $doc.ExportAsFixedFormat((Join-Path $PSScriptRoot 'original-render.pdf'), 17)
} finally {
    if ($null -ne $doc) { $doc.Close(0) }
    if ($null -ne $word) { $word.Quit() }
}
