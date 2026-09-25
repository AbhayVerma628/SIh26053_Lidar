$pptxPath = "C:\Users\HP\Desktop\SIH26053_TeraPulse_Official_Presentation.pptx"
$pdfPath = "C:\Users\HP\Desktop\SIH26053_TeraPulse_Official_Presentation.pdf"

$ppt = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $ppt.Presentations.Open($pptxPath, 1, 0, 0)
    $presentation.SaveAs($pdfPath, 32) # 32 = ppSaveAsPDF
    $presentation.Close()
    Write-Host "PDF Exported Successfully: $pdfPath"
} finally {
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
