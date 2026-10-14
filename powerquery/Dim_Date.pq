// ============================================================
// Dim_Date.pq  —  Power Query M for the Date dimension table
// ============================================================
// Generates a continuous calendar from 2023-01-01 to 2024-12-31.
// After loading in Power BI, mark this table as a Date Table:
//   Table Tools → Mark as Date Table → Date column
// HOW TO USE:
//   1. Power Query Editor → New Source → Blank Query
//   2. Home → Advanced Editor → paste this script
//   3. Rename query to "Dim_Date"
// ============================================================

let
    // ── Parameters ───────────────────────────────────────────
    StartDate = #date(2023, 1, 1),
    EndDate   = #date(2024, 12, 31),

    // ── Generate list of dates ───────────────────────────────
    DayCount  = Duration.Days(EndDate - StartDate) + 1,
    DateList  = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    DateTable = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),

    // ── Set Date type ────────────────────────────────────────
    TypedDate = Table.TransformColumnTypes(DateTable, {{"Date", type date}}),

    // ── Add calendar columns ─────────────────────────────────
    WithYear = Table.AddColumn(TypedDate, "Year",
        each Date.Year([Date]), Int64.Type),

    WithQuarter = Table.AddColumn(WithYear, "Quarter",
        each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),

    WithMonth = Table.AddColumn(WithQuarter, "Month_Number",
        each Date.Month([Date]), Int64.Type),

    WithMonthName = Table.AddColumn(WithMonth, "Month_Name",
        each Date.ToText([Date], "MMMM"), type text),

    WithMonthShort = Table.AddColumn(WithMonthName, "Month_Short",
        each Date.ToText([Date], "MMM"), type text),

    WithYearMonth = Table.AddColumn(WithMonthShort, "Year_Month",
        each Text.From(Date.Year([Date])) & "-"
          & Text.PadStart(Text.From(Date.Month([Date])), 2, "0"),
        type text),

    WithWeek = Table.AddColumn(WithYearMonth, "Week_Number",
        each Date.WeekOfYear([Date]), Int64.Type),

    WithDayName = Table.AddColumn(WithWeek, "Day_Name",
        each Date.ToText([Date], "dddd"), type text),

    WithDayOfWeek = Table.AddColumn(WithDayName, "Day_Of_Week",
        each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),

    WithIsWeekend = Table.AddColumn(WithDayOfWeek, "Is_Weekend",
        each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical),

    // ── Sort by Date ─────────────────────────────────────────
    Sorted = Table.Sort(WithIsWeekend, {{"Date", Order.Ascending}})

in
    Sorted
