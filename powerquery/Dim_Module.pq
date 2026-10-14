// ============================================================
// Dim_Module.pq  —  Power Query M for the Module dimension
// ============================================================
// Unions all Module values from Defects, Issues, Risks, and Reviews
// to produce a single, deduplicated module list.
// HOW TO USE:
//   1. Load ALL four fact tables first (Defects, Issues, Risks, Reviews)
//   2. New Source → Blank Query
//   3. Advanced Editor → paste this script
//   4. Rename query to "Dim_Module"
// ============================================================

let
    // ── Collect Module values from each fact table ───────────
    // ASSUMPTION: Each fact table is already loaded as a Power Query table
    // with at least a "Module" column.

    FromDefects = Table.SelectColumns(Defects, {"Module"}),
    FromIssues  = Table.SelectColumns(Issues,  {"Module"}),
    FromRisks   = Table.SelectColumns(Risks,   {"Module"}),
    FromReviews = Table.SelectColumns(Reviews, {"Module"}),

    // ── Union all ────────────────────────────────────────────
    Unioned = Table.Combine({FromDefects, FromIssues, FromRisks, FromReviews}),

    // ── Deduplicate ──────────────────────────────────────────
    Distinct = Table.Distinct(Unioned),

    // ── Set type ─────────────────────────────────────────────
    TypedTable = Table.TransformColumnTypes(
        Distinct, {{"Module", type text}}
    ),

    // ── Add a Module_Key for potential integer FK joins ───────
    WithKey = Table.AddIndexColumn(TypedTable, "Module_Key", 1, 1, Int64.Type),

    // ── Add display name (same as Module for now) ─────────────
    WithDisplay = Table.AddColumn(
        WithKey, "Module_Display", each [Module], type text
    ),

    Sorted = Table.Sort(WithDisplay, {{"Module", Order.Ascending}})

in
    Sorted
