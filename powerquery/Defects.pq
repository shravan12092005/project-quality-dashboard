// ============================================================
// Defects.pq  —  Power Query M for the Defects fact table
// ============================================================
// HOW TO USE:
//   1. In Power BI Desktop → Home → Transform Data → Power Query Editor
//   2. New Source → Blank Query
//   3. Home → Advanced Editor → paste this entire script
//   4. Update the filePath variable below to your absolute path
//   5. Click Done → rename query to "Defects"
// ============================================================

let
    // ── 1. Load CSV ──────────────────────────────────────────
    filePath = "C:\YOUR_PATH\project-quality-dashboard\data\clean\defects_clean.csv",
    // Replace the path above with your actual path.
    // Tip: right-click the file in Explorer → Copy as path → paste here

    Source = Csv.Document(
        File.Contents(filePath),
        [Delimiter = ",", Columns = 20, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),

    // ── 2. Promote first row to headers ──────────────────────
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // ── 3. Set column data types ─────────────────────────────
    TypedTable = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"Defect_ID",               type text},
            {"Project",                 type text},
            {"Phase",                   type text},
            {"Module",                  type text},
            {"Severity",                type text},
            {"Priority",                type text},
            {"Status",                  type text},
            {"Root_Cause",              type text},
            {"Operating_System",        type text},
            {"Created_Date",            type date},
            {"Closed_Date",             type date},
            {"Is_Closed",               Int64.Type},
            {"Resolution_Time_Original",Int64.Type},
            {"Defect_Age",              Int64.Type},
            {"Data_Quality_Flag",       Int64.Type},
            {"Month",                   type text},
            {"Resolution_Days",         Int64.Type},
            {"SLA_Target_Days",         Int64.Type},
            {"SLA_Met",                 type logical},
            {"Is_Overdue",              type logical}
        }
    ),

    // ── 4. Add a Defect_Key integer surrogate (optional for perf) ──
    // This is optional; Power BI can use Defect_ID as the key.
    // Uncomment if you want an integer surrogate key.
    // WithKey = Table.AddIndexColumn(TypedTable, "Defect_Key", 1, 1, Int64.Type),

    // ── 5. Filter out Data_Quality_Flag = 1 rows from KPIs?
    // DECISION: Keep flagged rows but mark them.
    // To exclude them from all visuals, uncomment the next line:
    // FilteredRows = Table.SelectRows(TypedTable, each [Data_Quality_Flag] = 0),

    FinalTable = TypedTable

in
    FinalTable
