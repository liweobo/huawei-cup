$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$outDir=Join-Path $PSScriptRoot 'equation-previews'
$items=Get-ChildItem -LiteralPath $outDir -Filter 'preview-*.wmf'
$canvas=New-Object System.Drawing.Bitmap(1100,([math]::Ceiling($items.Count / 4) * 100))
$g=[System.Drawing.Graphics]::FromImage($canvas)
$g.Clear([System.Drawing.Color]::White)
$font=New-Object System.Drawing.Font('Arial',12)
$index=0
foreach ($item in $items) {
    $m=[System.Drawing.Imaging.Metafile]::new($item.FullName)
    $x=($index % 4)*275
    $y=[math]::Floor($index/4)*100
    $g.DrawString(('{0:D3}' -f ($index+1)),$font,[System.Drawing.Brushes]::Blue,$x+5,$y+5)
    $scale=[math]::Min(210.0/$m.Width,50.0/$m.Height)
    $g.DrawImage($m,([single]($x+45)),([single]($y+25)),([single]($m.Width*$scale)),([single]($m.Height*$scale)))
    $m.Dispose()
    $index++
}
$canvas.Save((Join-Path $outDir 'equation-contact-sheet.png'),[System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $canvas.Dispose(); $font.Dispose()
