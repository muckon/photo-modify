param(
 [Parameter(Mandatory=$true)][string]$DeckPath,
 [Parameter(Mandatory=$true)][string]$OutputDir,
 [int]$Width=1200,
 [int]$Height=2000
)
$ErrorActionPreference='Stop'
$skillPath=[IO.Path]::GetFullPath((Split-Path -Parent $PSScriptRoot))
$previewPath=[IO.Path]::GetFullPath($OutputDir)
if($previewPath.Equals($skillPath,[StringComparison]::OrdinalIgnoreCase) -or $previewPath.StartsWith($skillPath+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){
 throw 'Runtime output must be outside the skill installation.'
}
if(Test-Path -LiteralPath $previewPath){throw 'Preview directory already exists; choose a new directory.'}
if($Width -le 0 -or $Height -le 0){throw 'Preview dimensions must be positive.'}
$resolvedDeck=(Resolve-Path -LiteralPath $DeckPath).Path
New-Item -ItemType Directory -Path $previewPath | Out-Null
$app=$null;$document=$null;$initialCount=0
try{
 $app=New-Object -ComObject PowerPoint.Application
 $initialCount=$app.Presentations.Count
 # ReadOnly, Untitled and WithWindow: open an isolated read-only copy.
 $document=$app.Presentations.Open($resolvedDeck,-1,-1,0)
 $pageWidth=$document.PageSetup.SlideWidth;$pageHeight=$document.PageSetup.SlideHeight
 if([Math]::Abs(($Width/[double]$Height)/($pageWidth/[double]$pageHeight)-1) -gt 0.01){throw 'Preview dimensions do not match the slide aspect ratio.'}
 $summary=@()
 for($index=1;$index -le $document.Slides.Count;$index++){
  $slide=$document.Slides.Item($index)
  $slide.Export((Join-Path $previewPath ('slide-{0:D3}.png' -f $index)),'PNG',$Width,$Height)
  $texts=0
  foreach($shape in $slide.Shapes){if($shape.HasTextFrame -and $shape.TextFrame.HasText){$texts++}}
  $summary += [PSCustomObject]@{Slide=$index;Shapes=$slide.Shapes.Count;EditableTextBoxes=$texts}
 }
 $summary | ConvertTo-Json
}finally{
 if($document){try{$document.Saved=-1;$document.Close()}finally{[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)}}
 if($app){
  if($initialCount -eq 0 -and $app.Presentations.Count -eq 0){$app.Quit()}
  [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($app)
 }
}
