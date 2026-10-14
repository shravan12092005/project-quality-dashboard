// ============================================================
// Issues.pq  —  Power Query M for the Issues fact table
// ============================================================
// HOW TO USE:
//   1. Power Query Editor → New Source → Blank Query
//   2. Home → Advanced Editor → paste this script
//   3. Update filePath → rename query to "Issues"
// ============================================================

let
    filePath = "C:\YOUR_PATH\project-quality-dashboard\data\clean\issues_clean.csv",

    Source = Csv.Document(
        File.Contents(filePath),
        [Delimiter = ",", Columns = 14, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),

    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    TypedTable = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"Issue_ID",        type text},
            {"Project",         type text},
            {"Phase",           type text},
            {"Module",          type text},
            {"Type",            type text},
            {"Severity",        type text},
            {"Status",          type text},
            {"Owner",           type text},
            {"Root_Cause",      type text},
            {"Quality_Gate",    type text},
            {"Created_Date",    type date},
            {"Due_Date",        type date},
            {"Closed_Date",     type date},
            {"Is_Overdue",      type logical},
            {"Month",           type text}
        }
    )

in
    TypedTable
