// ============================================================
// Dim_Severity.pq  —  Power Query M for the Severity dimension
// ============================================================
// Static table with severity labels and SLA target days.
// SLA_Target_Days are a documented assumption (see NOTICE):
//   Critical = 2 days   (P1 severity — immediate response)
//   High     = 5 days   (P2 severity — 1 business week)
//   Medium   = 10 days  (P3 severity — 2 business weeks)
//   Low      = 20 days  (P4 severity — 1 business month)
// HOW TO USE:
//   1. Power Query Editor → New Source → Blank Query
//   2. Home → Advanced Editor → paste this script
//   3. Rename query to "Dim_Severity"
// ============================================================

let
    // ── Define static severity table ─────────────────────────
    Source = Table.FromRows(
        {
            {1, "Critical", 2,  "#C0392B"},  // Red
            {2, "High",     5,  "#E67E22"},  // Orange
            {3, "Medium",   10, "#F1C40F"},  // Yellow
            {4, "Low",      20, "#27AE60"}   // Green
        },
        {
            "Severity_Rank",
            "Severity",
            "SLA_Target_Days",
            "Severity_Color"
        }
    ),

    TypedTable = Table.TransformColumnTypes(
        Source,
        {
            {"Severity_Rank",    Int64.Type},
            {"Severity",         type text},
            {"SLA_Target_Days",  Int64.Type},
            {"Severity_Color",   type text}
        }
    )

in
    TypedTable
