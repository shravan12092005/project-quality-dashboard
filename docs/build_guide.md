# Build Guide — Project Quality Dashboard
## Click-by-Click Instructions for Power BI Desktop

> **Prerequisite**: Power BI Desktop installed (free from Microsoft Store or powerbi.microsoft.com).  
> **Time estimate**: 3–4 hours for a complete first build.

---

## Step 0: Prepare Your Files

1. Run `python scripts/gen.py` from the `project-quality-dashboard/` directory.
2. Run `python scripts/clean_data.py` — verify it prints no errors and all 4 clean CSVs appear in `data/clean/`.
3. Note the **absolute path** to `project-quality-dashboard/data/clean/` on your Windows machine.  
   Example: `C:\Users\YourName\Documents\project-quality-dashboard\data\clean\`

---

## Step 1: Load Data via Power Query

### 1.1 Open Power BI Desktop → New Report

### 1.2 Load each table using Advanced Editor

For each table below:
1. **Home → Transform Data** to open Power Query Editor.
2. **New Source → Blank Query**.
3. **Home → Advanced Editor**.
4. **Delete all existing text** in the editor.
5. **Paste** the contents of the corresponding `.pq` file from the `powerquery/` folder.
6. **Update the `filePath` variable** at the top to your actual Windows path.
7. Click **Done**.
8. In the Queries panel on the left, **right-click → Rename** to the table name.

| Query Name | .pq File |
|-----------|----------|
| `Defects` | `powerquery/Defects.pq` |
| `Issues` | `powerquery/Issues.pq` |
| `Risks` | `powerquery/Risks.pq` |
| `Reviews` | `powerquery/Reviews.pq` |
| `Dim_Date` | `powerquery/Dim_Date.pq` |
| `Dim_Module` | `powerquery/Dim_Module.pq` |
| `Dim_Severity` | `powerquery/Dim_Severity.pq` |

> ⚠️ **Load `Defects`, `Issues`, `Risks`, and `Reviews` BEFORE `Dim_Module`**, because `Dim_Module.pq` references those queries by name.

### 1.3 Close & Apply

**Home → Close & Apply** — wait for all tables to load.

---

## Step 2: Build the Data Model

1. Click the **Model view** icon (third icon on the left sidebar, looks like a diagram).
2. You will see all 7 tables. Arrange them: Dim tables at top, Fact tables at bottom.

### 2.1 Create Relationships

Create the following relationships by **dragging** from the fact table column to the dimension column:

| From Table | From Column | To Table | To Column | Active? |
|-----------|------------|---------|----------|---------|
| Defects | Created_Date | Dim_Date | Date | ✅ Active |
| Defects | Closed_Date | Dim_Date | Date | ❌ Inactive |
| Defects | Module | Dim_Module | Module | ✅ Active |
| Defects | Severity | Dim_Severity | Severity | ✅ Active |
| Issues | Created_Date | Dim_Date | Date | ✅ Active |
| Issues | Module | Dim_Module | Module | ✅ Active |
| Risks | Created_Date | Dim_Date | Date | ✅ Active |
| Risks | Module | Dim_Module | Module | ✅ Active |
| Reviews | Scheduled_Date | Dim_Date | Date | ✅ Active |
| Reviews | Module | Dim_Module | Module | ✅ Active |

> For the **inactive** `Defects[Closed_Date] → Dim_Date[Date]` relationship:  
> After dragging, double-click the relationship line → uncheck **Active** → OK.  
> The `[Defects Closed by Month]` DAX measure uses `USERELATIONSHIP()` to activate it on demand.

### 2.2 Mark Date Table

1. Click on the **Dim_Date** table.
2. **Table Tools → Mark as Date Table → Mark as Date Table**.
3. Select **Date** column → OK.

### 2.3 Set Cardinality

All relationships should be **Many-to-One (Many side = Fact table)** with **Single** cross-filter direction. Verify by double-clicking each relationship line.

---

## Step 3: Create Measures Table

1. **Home → Enter Data** → name the table `_Measures` → 1 column, 1 row (type any placeholder).
2. Click **Load**.
3. In the **Fields pane**, right-click `_Measures` → **New Measure** for each DAX measure below.

### 3.1 Add All DAX Measures

Copy each measure from `dax/measures.dax`. For each:
1. Right-click `_Measures` → **New Measure**.
2. In the formula bar, **delete** the default `Measure =` text.
3. **Paste** the measure formula (just the right-hand side; the name goes in the `Name` field at the top-left).
4. Press **Enter**.
5. In the **Properties pane** (right side), set **Display Folder** as shown in the table below.

| Measure Name | Display Folder |
|-------------|---------------|
| Total Defects | Defect KPIs |
| Open Defects | Defect KPIs |
| Closed Defects | Defect KPIs |
| Deferred Defects | Defect KPIs |
| Closure Rate % | Defect KPIs |
| Avg Resolution Days | Defect KPIs |
| Defects Created by Month | Time Intelligence |
| Defects Closed by Month | Time Intelligence |
| Cumulative Backlog | Time Intelligence |
| SLA Compliance % | Quality KPIs |
| Open Action Items | Action Items |
| Overdue Action Items | Action Items |
| Avg Risk Score | Risk KPIs |
| High Risks | Risk KPIs |
| Review Completion % | Review KPIs |
| Overdue Reviews | Review KPIs |
| Audit Findings Open | Audit KPIs |

---

## Step 4: Colour Palette

Use this consistent palette across all pages:

| Use | Hex | Description |
|----|-----|-------------|
| Background | `#0F1117` | Dark navy |
| Card background | `#1A1D2E` | Slightly lighter |
| Accent / Primary | `#4F8EF7` | Electric blue |
| Critical | `#E63946` | Red |
| High | `#F4A261` | Orange |
| Medium | `#E9C46A` | Amber |
| Low | `#52B788` | Green |
| Neutral text | `#CBD5E1` | Light grey |
| Subtle border | `#2D3250` | Dark border |

---

## Step 5: Page 1 — Executive Summary

### Layout Grid (1280×720 canvas)
```
┌──────────────────────────────────────────────────────────┐
│  [Logo / Title]          [Date Slicer]                   │
│                          [Module Slicer] [Severity Slicer]│
├──────┬──────┬──────┬──────┬──────────────────────────────┤
│ KPI  │ KPI  │ KPI  │ KPI  │  KPI                         │
│Card 1│Card 2│Card 3│Card 4│  Card 5                       │
├──────────────────────────┬───────────────────────────────┤
│  Created vs Closed Line  │  Cumulative Backlog Area Chart │
└──────────────────────────┴───────────────────────────────┘
```

### 5.1 Title Text Box
- Insert → Text Box → `Project Quality Dashboard`
- Font: Segoe UI Semibold, size 18, colour `#4F8EF7`

### 5.2 KPI Cards (5 cards)

For each card:
1. **Visualizations → Card** visual.
2. Drag the measure into the **Fields** well.
3. In **Format visual**: turn on **Call-out value**, set font size to 32, colour = accent.
4. Set **Label** (below the number) to the measure name.

| Card | Measure | Format |
|------|---------|--------|
| 1 | Total Defects | Integer |
| 2 | Open Defects | Integer |
| 3 | Closure Rate % | "0.0%" |
| 4 | Avg Resolution Days | "0.0 days" |
| 5 | SLA Compliance % | "0.0%" |

> Tip: Set card background to `#1A1D2E`, border radius 8px, no border.

### 5.3 Slicers (3 slicers)

| Slicer | Field | Style |
|--------|-------|-------|
| Date range | Dim_Date[Year_Month] | Dropdown or Between |
| Module | Dim_Module[Module] | Dropdown, multi-select |
| Severity | Dim_Severity[Severity] | Dropdown, multi-select |

### 5.4 Line Chart — Created vs Closed
- Visual type: **Line chart**
- X-axis: `Dim_Date[Year_Month]`
- Y-axis: `[Defects Created by Month]`, `[Defects Closed by Month]`
- Line colours: Created = `#4F8EF7`, Closed = `#52B788`
- Title: "Defects Created vs Closed — Monthly"
- Tooltip: Month, Created count, Closed count

### 5.5 Area Chart — Backlog Trend
- Visual type: **Area chart**
- X-axis: `Dim_Date[Year_Month]`
- Y-axis: `[Cumulative Backlog]`
- Area fill: gradient from `#4F8EF7` (top) to transparent (bottom)
- Title: "Cumulative Defect Backlog"
- Tooltip: Month, Backlog count

---

## Step 6: Page 2 — Defect Analysis

### Layout Grid
```
┌─────────────────────┬────────────────────────────────────┐
│   Severity Donut    │   Defects by Module (Bar)           │
├─────────────────────┴─────────┬────────────────────────── ┤
│  Module × Severity Matrix     │ Resolution Time by Severity│
└───────────────────────────────┴───────────────────────────┘
```

### 6.1 Severity Donut Chart
- Visual type: **Donut chart**
- Legend: `Defects[Severity]`
- Values: `[Total Defects]`
- Colours: Critical=`#E63946`, High=`#F4A261`, Medium=`#E9C46A`, Low=`#52B788`
- Title: "Defects by Severity"
- Tooltip: Severity, Count, % of Total

### 6.2 Defects by Module (Bar Chart)
- Visual type: **Clustered bar chart** (horizontal)
- Y-axis: `Dim_Module[Module]`
- X-axis: `[Total Defects]`
- Colour: `#4F8EF7`
- Sort: Descending by Total Defects
- Title: "Defects by Module"
- Tooltip: Module, Count, % of Total

### 6.3 Module × Severity Matrix Heatmap
- Visual type: **Matrix**
- Rows: `Defects[Module]`
- Columns: `Defects[Severity]` (sort by Severity_Rank from Dim_Severity)
- Values: `[Total Defects]`
- Conditional Formatting: Background colour on Values — white → `#E63946` scale
- Title: "Defect Density Heatmap (Module × Severity)"

### 6.4 Resolution Time by Severity (Bar)
- Visual type: **Clustered bar chart**
- Y-axis: `Dim_Severity[Severity]`
- X-axis: `[Avg Resolution Days]`
- Add a **constant line** for SLA target days per severity (use Analytics pane → Reference line, one per severity)
- Title: "Avg Resolution Days vs SLA Target"
- Tooltip: Severity, Avg Days, SLA Target

---

## Step 7: Page 3 — Risks & Reviews

### Layout Grid
```
┌──────────────────────────────┬─────────────────────────── ┐
│  Risk Heatmap (Scatter)      │  Risks by Status (Bar)      │
├──────────────────────────────┼────────────────────────────┤
│  Review Status by Type (Bar) │  Overdue Reviews (Table)    │
└──────────────────────────────┴────────────────────────────┘
```

### 7.1 Risk Probability × Impact Scatter Heatmap
- Visual type: **Scatter chart**
- X-axis: `Risks[Probability]` (1–5)
- Y-axis: `Risks[Impact]` (1–5)
- Size: `Risks[Risk_Score]`
- Details: `Risks[Risk_ID]`
- Colour: `Risks[Category]`
- Title: "Risk Register — Probability vs Impact"
- Tooltip: Risk_ID, Category, Probability, Impact, Risk_Score, Status
- Add a **reference line** at X=3, Y=3 (manual shape) to delineate red/green zones.

### 7.2 Risks by Status (Bar)
- Visual type: **Clustered bar chart**
- Y-axis: `Risks[Status]`
- X-axis: `COUNTROWS(Risks)` — use a simple count measure
- Title: "Risks by Status"

### 7.3 Review Status by Type (Stacked Bar)
- Visual type: **Stacked bar chart**
- Y-axis: `Reviews[Review_Type]`
- X-axis: `COUNTROWS(Reviews)`
- Legend: `Reviews[Status]`
- Status colours: Completed=`#52B788`, In Progress=`#4F8EF7`, Planned=`#E9C46A`, Overdue=`#E63946`
- Title: "Reviews by Type and Status"

### 7.4 Overdue Reviews Table
- Visual type: **Table**
- Columns: `Reviews[Review_ID]`, `Reviews[Module]`, `Reviews[Review_Type]`, `Reviews[Scheduled_Date]`, `Reviews[Owner]`
- Filter: `Reviews[Is_Overdue] = TRUE`
- Conditional formatting: Scheduled_Date column → red background if overdue
- Title: "Overdue Reviews"

---

## Step 8: Page 4 — Action Items & Audit Findings

### Layout Grid
```
┌──────────────────────────────────────────────────────────┐
│  KPI Card: Open Action Items  │  KPI Card: Overdue AI    │
│  KPI Card: Audit Findings Open                           │
├───────────────────────────────┬──────────────────────────┤
│  Overdue Action Items (Table) │  Findings by Quality Gate │
├───────────────────────────────┼──────────────────────────┤
│  Root Cause Bar               │                          │
└───────────────────────────────┴──────────────────────────┘
```

### 8.1 KPI Cards
| Card | Measure |
|------|---------|
| Open Action Items | `[Open Action Items]` |
| Overdue Action Items | `[Overdue Action Items]` |
| Audit Findings Open | `[Audit Findings Open]` |

### 8.2 Overdue Action Items Table
- Visual type: **Table**
- Filter: `Issues[Type] = "Action Item"` AND `Issues[Is_Overdue] = TRUE`
- Columns: `Issues[Issue_ID]`, `Issues[Module]`, `Issues[Severity]`, `Issues[Due_Date]`, `Issues[Owner]`, `Issues[Status]`
- Sort: `Due_Date` ascending (oldest overdue first)
- Conditional formatting: Severity column → colour by value

### 8.3 Findings by Quality Gate (Bar)
- Visual type: **Clustered bar chart**
- Filter: `Issues[Type]` = "Audit Finding"
- X-axis: `[Audit Findings Open]`
- Y-axis: `Issues[Quality_Gate]`
- Title: "Audit Findings by Quality Gate"

### 8.4 Root Cause Bar
- Visual type: **Clustered bar chart**
- X-axis: `[Total Defects]`
- Y-axis: `Defects[Root_Cause]`
- Sort: descending
- Title: "Defects by Root Cause"

---

## Step 9: Formatting & Polish

1. **Set report theme**: View → Themes → Browse → import a dark JSON theme, or manually set canvas background to `#0F1117` for all pages.
2. **Page navigation**: Insert → Buttons → Navigation → for each page add a button linking to that page.
3. **Consistent fonts**: All titles → Segoe UI, 12pt, `#CBD5E1`. All card values → Segoe UI Semibold, 32pt, `#4F8EF7`.
4. **Visual borders**: All visuals → Format → Visual border → `#2D3250`, rounded corners 8px.
5. **Tooltips**: Verify each tooltip shows the right fields (see per-visual notes above).

---

## Step 10: Save and Export

1. **File → Save** → save as `project-quality-dashboard.pbix`.
2. For portfolio: take screenshots of each page and add to `docs/screenshots/`.
3. For README: update the Screenshots section with real image paths.

---

## Assumptions Made in This Build

| # | Assumption | Where It Appears |
|---|-----------|-----------------|
| A1 | SLA days: Critical=2, High=5, Medium=10, Low=20 | Dim_Severity, SLA_Met column, [SLA Compliance %] |
| A2 | Severity 1=Critical, 2=High, 3=Medium, 4=Low | clean_data.py severity mapping |
| A3 | Status nulls inferred from Is_Closed flag | clean_data.py |
| A4 | Re-Opened counts as Open for KPI purposes | [Open Defects] measure |
| A5 | Deferred tracked separately, not Open or Closed | [Deferred Defects], excluded from [Open Defects] |
| A6 | Synthetic data uses same Project/Module values as Defects | gen.py |
| A7 | Dim_Date spans 2023-01-01 to 2024-12-31 | Dim_Date.pq |
| A8 | High Risk = Risk_Score ≥ 15 (standard 5×5 matrix red zone) | [High Risks] measure |
| A9 | Issues table holds Action Items, Audit Findings, and Review Findings as a combined fact | Issues.pq, all Issues measures |
