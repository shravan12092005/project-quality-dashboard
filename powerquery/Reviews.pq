// ============================================================
// Reviews.pq  —  Power Query M for the Reviews fact table
// ============================================================
// HOW TO USE:
//   1. Power Query Editor → New Source → Blank Query
//   2. Home → Advanced Editor → paste this script
//   3. Update filePath → rename query to "Reviews"
// ============================================================

let
    filePath = "C:\YOUR_PATH\project-quality-dashboard\data\clean\reviews_clean.csv",

    Source = Csv.Document(
        File.Contents(filePath),
        [Delimiter = ",", Columns = 12, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),

    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    TypedTable = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"Review_ID",           type text},
            {"Project",             type text},
            {"Module",              type text},
            {"Review_Type",         type text},
            {"Status",              type text},
            {"Owner",               type text},
            {"Scheduled_Date",      type date},
            {"Completed_Date",      type date},
            {"Findings_Count",      Int64.Type},
            {"Phase",               type text},
            {"Date_Order_Flag",     type logical},
            {"Is_Overdue",          type logical}
        }
    )

in
    TypedTable
