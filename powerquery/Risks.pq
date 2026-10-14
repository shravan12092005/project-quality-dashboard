// ============================================================
// Risks.pq  —  Power Query M for the Risks fact table
// ============================================================
// HOW TO USE:
//   1. Power Query Editor → New Source → Blank Query
//   2. Home → Advanced Editor → paste this script
//   3. Update filePath → rename query to "Risks"
// ============================================================

let
    filePath = "C:\YOUR_PATH\project-quality-dashboard\data\clean\risks_clean.csv",

    Source = Csv.Document(
        File.Contents(filePath),
        [Delimiter = ",", Columns = 13, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),

    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    TypedTable = Table.TransformColumnTypes(
        PromotedHeaders,
        {
            {"Risk_ID",         type text},
            {"Project",         type text},
            {"Module",          type text},
            {"Category",        type text},
            {"Probability",     Int64.Type},
            {"Impact",          Int64.Type},
            {"Risk_Score",      Int64.Type},
            {"Status",          type text},
            {"Owner",           type text},
            {"Created_Date",    type date},
            {"Review_Date",     type date},
            {"Description",     type text},
            {"Is_High_Risk",    type logical}
        }
    )

in
    TypedTable
