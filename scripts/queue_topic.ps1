# Helper script to queue a custom topic/keyword to upcoming_topics.json
param (
    [Parameter(Mandatory=$true)]
    [string]$Topic
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$baseDir = Split-Path -Parent $scriptDir
$upcomingJsonPath = Join-Path $baseDir "data\upcoming_topics.json"

if (-not (Test-Path $upcomingJsonPath)) {
    Write-Error "Could not find $upcomingJsonPath"
    exit 1
}

$upcoming = Get-Content $upcomingJsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

$newEntry = [PSCustomObject]@{
    id = "custom-$((Get-Date).Ticks)"
    topic = $Topic
    level = "SPECIAL DISPATCH: $($Topic.ToUpper())"
    levelClass = "level-3"
    readTime = "8 min read"
    audience = "Enterprise Engineers & Architects"
    title = "$Topic in Enterprise Claude Architecture"
    lead = "Deep dive into $Topic: architectural patterns, tradeoffs, and production reliability for senior engineers."
    stats = [PSCustomObject]@{
        type = "info"
        title = "Industry Impact of $Topic:"
        items = @(
            "Adopting structured $Topic standards reduces runtime defects by over 40%.",
            "Improves system observability and reliability across distributed workflows."
        )
    }
    mentalModel = [PSCustomObject]@{
        title = "1. The 60-Second Mental Model: $Topic"
        text = "Applying systems engineering rigor to $Topic ensures predictable, observable, and resilient Claude deployments."
    }
    diagram = "graph LR`n    A[Client Query] --> B[Claude $Topic Engine]`n    B --> C[Validated Response]`n    style B fill:#1e3a8a,stroke:#60a5fa,color:#fff"
    diagramCaption = "Figure: Operational Flow for $Topic"
    codeTitle = "enterprise_scaffold.py"
    codeContent = "# Production Architecture Implementation for $Topic`n# Enforce XML validation and structured contracts across execution boundaries."
    takeaway = [PSCustomObject]@{
        title = "Key Takeaways"
        items = @(
            "Incorporate $Topic principles into prompt design reviews.",
            "Establish automated evaluation baselines before releasing to production."
        )
        badge = "Disciplined architecture around $Topic creates enterprise value."
    }
}

# Prepend so it is next in line!
$updatedUpcoming = @($newEntry) + @($upcoming)
$jsonUpcoming = $updatedUpcoming | ConvertTo-Json -Depth 15
[System.IO.File]::WriteAllText($upcomingJsonPath, $jsonUpcoming, [System.Text.Encoding]::UTF8)

Write-Host "✅ Successfully queued '$Topic' as the NEXT post to publish!" -ForegroundColor Green
Write-Host "Total queued topics: $($updatedUpcoming.Count)" -ForegroundColor Cyan
