"""
clean_data.py  —  Data cleaning pipeline for Project Quality Dashboard
=======================================================================
Reads raw CSVs from data/raw/, applies quality fixes and derived columns,
validates integrity, prints a data-quality summary, and writes clean CSVs
to data/clean/.

Run from the project-quality-dashboard/ root:
    python scripts/clean_data.py

Outputs:
    data/clean/defects_clean.csv
    data/clean/issues_clean.csv
    data/clean/risks_clean.csv
    data/clean/reviews_clean.csv

Severity → SLA target days mapping (documented assumption A1):
    Critical  = 2 days
    High      = 5 days
    Medium    = 10 days
    Low       = 20 days

Deferred status is tracked separately (not Open, not Closed) per user decision.
Resolution time: both original (Resolution_Time_Original) and
recalculated (Resolution_Days) from date diff are preserved.
"""

import sys
from datetime import date
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("❌  pandas is not installed. Run: pip install pandas")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants / mappings ──────────────────────────────────────────────────────
SEVERITY_MAP = {
    "Severity 1": "Critical",
    "Severity 2": "High",
    "Severity 3": "Medium",
    "Severity 4": "Low",
}

# Canonical open-ish statuses (defect is still active)
OPEN_STATUSES = {"Open", "In Progress", "Re-Opened"}

# SLA target days per severity (Assumption A1)
SLA_TARGET = {
    "Critical": 2,
    "High": 5,
    "Medium": 10,
    "Low": 20,
}

DATE_FMT = "%d-%m-%Y"


def parse_date_col(series: pd.Series, col_name: str) -> pd.Series:
    """Parse DD-MM-YYYY string dates; warn on failures."""
    parsed = pd.to_datetime(series, format=DATE_FMT, errors="coerce")
    n_failed = parsed.isna().sum() - series.isna().sum()
    if n_failed > 0:
        print(f"    ⚠  {col_name}: {n_failed} rows could not be parsed as dates → set NaT")
    return parsed


# ── Separator helper ──────────────────────────────────────────────────────────
def section(title: str):
    print(f"\n{'═'*60}")
    print(f"  {title}")
    print(f"{'═'*60}")


# ══════════════════════════════════════════════════════════════════════════════
# 1. DEFECTS
# ══════════════════════════════════════════════════════════════════════════════
section("1 / 4  Cleaning  defects")

df = pd.read_csv(RAW_DIR / "Processed_QA_Defects.csv", dtype=str)
print(f"  Raw rows  : {len(df):,}")

# ── Rename Resolution_Time to preserve original ────────────────────────────
df = df.rename(columns={"Resolution_Time": "Resolution_Time_Original"})

# ── Parse dates ────────────────────────────────────────────────────────────
df["Created_Date"] = parse_date_col(df["Created_Date"], "Created_Date")
df["Closed_Date"] = parse_date_col(df["Closed_Date"], "Closed_Date")

# ── Map Severity (Severity 1 → Critical, etc.) ────────────────────────────
pre_sev_nulls = df["Severity"].isna().sum()
df["Severity"] = df["Severity"].map(SEVERITY_MAP)
post_sev_nulls = df["Severity"].isna().sum()
if post_sev_nulls > pre_sev_nulls:
    print(f"    ⚠  {post_sev_nulls - pre_sev_nulls} Severity values did not match map → NaN")

# ── Standardise Status ────────────────────────────────────────────────────
# Re-open → Re-Opened; fill nulls by inference from Is_Closed
df["Is_Closed"] = df["Is_Closed"].astype(str).str.strip()
df["Status"] = df["Status"].str.strip()
df["Status"] = df["Status"].replace("Re-open", "Re-Opened")
# Fill null Status based on Is_Closed flag
null_status_mask = df["Status"].isna() | (df["Status"] == "")
n_inferred = null_status_mask.sum()
df.loc[null_status_mask & (df["Is_Closed"] == "1"), "Status"] = "Closed"
df.loc[null_status_mask & (df["Is_Closed"] == "0"), "Status"] = "Open"
print(f"  Status nulls inferred from Is_Closed: {n_inferred}")

# ── Fill other nulls ───────────────────────────────────────────────────────
n_module_null = df["Module"].isna().sum()
df["Module"] = df["Module"].fillna("Unknown")
print(f"  Module nulls filled with 'Unknown': {n_module_null}")

n_rc_null = df["Root_Cause"].isna().sum()
df["Root_Cause"] = df["Root_Cause"].fillna("Unclassified")
print(f"  Root_Cause nulls filled with 'Unclassified': {n_rc_null}")

# ── Derived columns ────────────────────────────────────────────────────────
# Month (YYYY-MM) from Created_Date
df["Month"] = df["Created_Date"].dt.to_period("M").astype(str)

# Resolution_Days: (Closed_Date - Created_Date) in days
df["Resolution_Days"] = (df["Closed_Date"] - df["Created_Date"]).dt.days

# SLA_Target_Days from Severity
df["SLA_Target_Days"] = df["Severity"].map(SLA_TARGET)

# SLA_Met: True only if defect is Closed AND Resolution_Days <= SLA_Target_Days
df["SLA_Met"] = (
    (df["Status"] == "Closed")
    & df["Resolution_Days"].notna()
    & df["SLA_Target_Days"].notna()
    & (df["Resolution_Days"] <= df["SLA_Target_Days"])
)

# Is_Overdue: open defects where Defect_Age > SLA_Target_Days
df["Defect_Age"] = pd.to_numeric(df["Defect_Age"], errors="coerce")
df["Is_Overdue"] = (
    df["Status"].isin(OPEN_STATUSES)
    & df["Defect_Age"].notna()
    & df["SLA_Target_Days"].notna()
    & (df["Defect_Age"] > df["SLA_Target_Days"])
)

# ── Validation ─────────────────────────────────────────────────────────────
print("\n  ── Validation ──")
dup_ids = df["Defect_ID"].duplicated().sum()
assert dup_ids == 0, f"FAIL: {dup_ids} duplicate Defect_IDs found!"
print(f"  ✓ Duplicate Defect_IDs: {dup_ids}")

bad_dates = (
    df["Closed_Date"].notna()
    & (df["Closed_Date"] < df["Created_Date"])
).sum()
assert bad_dates == 0, f"FAIL: {bad_dates} rows where Closed_Date < Created_Date!"
print(f"  ✓ Closed_Date < Created_Date violations: {bad_dates}")

negative_res = (df["Resolution_Days"].notna() & (df["Resolution_Days"] < 0)).sum()
assert negative_res == 0, f"FAIL: {negative_res} rows with negative Resolution_Days!"
print(f"  ✓ Negative Resolution_Days: {negative_res}")

# ── Data-quality summary ───────────────────────────────────────────────────
print("\n  ── Data Quality Summary ──")
print(f"  Total rows              : {len(df):,}")
print(f"  Severity distribution   :\n{df['Severity'].value_counts().to_string()}")
print(f"  Status distribution     :\n{df['Status'].value_counts().to_string()}")
print(f"  SLA_Met (closed only)   : {df['SLA_Met'].sum()} / {(df['Status']=='Closed').sum()} closed defects")
print(f"  Overdue (open)          : {df['Is_Overdue'].sum()}")
print(f"  Avg Resolution_Days     : {df['Resolution_Days'].mean():.1f}")
print(f"  Data_Quality_Flag=1     : {(df['Data_Quality_Flag']=='1').sum()}")
print(f"  Remaining nulls per col :")
for col in df.columns:
    n = df[col].isna().sum()
    if n > 0:
        print(f"    {col:30s}: {n}")

# ── Write ──────────────────────────────────────────────────────────────────
out_path = CLEAN_DIR / "defects_clean.csv"
df.to_csv(out_path, index=False, date_format="%Y-%m-%d")
print(f"\n  ✓ Written → {out_path}  ({len(df):,} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# 2. ISSUES
# ══════════════════════════════════════════════════════════════════════════════
section("2 / 4  Cleaning  issues")

iss = pd.read_csv(RAW_DIR / "issues.csv", dtype=str)
print(f"  Raw rows: {len(iss):,}")

for col in ["Created_Date", "Due_Date", "Closed_Date"]:
    iss[col] = parse_date_col(iss[col], col)

# Validate no duplicate IDs
assert iss["Issue_ID"].duplicated().sum() == 0, "Duplicate Issue_IDs!"
print(f"  ✓ No duplicate Issue_IDs")

# Closed >= Created check
bad = (iss["Closed_Date"].notna() & (iss["Closed_Date"] < iss["Created_Date"])).sum()
assert bad == 0, f"{bad} issues have Closed_Date < Created_Date"
print(f"  ✓ No Closed_Date < Created_Date")

# Is_Overdue flag: Open/In Progress past Due_Date
today = pd.Timestamp(date.today())
iss["Is_Overdue"] = (
    iss["Status"].isin(["Open", "In Progress", "Overdue"])
    & iss["Due_Date"].notna()
    & (iss["Due_Date"] < today)
)

iss["Month"] = iss["Created_Date"].dt.to_period("M").astype(str)

print(f"  Status distribution:\n{iss['Status'].value_counts().to_string()}")
print(f"  Type distribution  :\n{iss['Type'].value_counts().to_string()}")
print(f"  Overdue issues     : {iss['Is_Overdue'].sum()}")

out_path = CLEAN_DIR / "issues_clean.csv"
iss.to_csv(out_path, index=False, date_format="%Y-%m-%d")
print(f"  ✓ Written → {out_path}  ({len(iss):,} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. RISKS
# ══════════════════════════════════════════════════════════════════════════════
section("3 / 4  Cleaning  risks")

rsk = pd.read_csv(RAW_DIR / "risks.csv", dtype=str)
print(f"  Raw rows: {len(rsk):,}")

for col in ["Created_Date", "Review_Date"]:
    rsk[col] = parse_date_col(rsk[col], col)

rsk["Probability"] = pd.to_numeric(rsk["Probability"], errors="coerce")
rsk["Impact"] = pd.to_numeric(rsk["Impact"], errors="coerce")
rsk["Risk_Score"] = pd.to_numeric(rsk["Risk_Score"], errors="coerce")

# Re-derive Risk_Score to validate
rsk["Risk_Score_Derived"] = rsk["Probability"] * rsk["Impact"]
mismatch = (rsk["Risk_Score"] != rsk["Risk_Score_Derived"]).sum()
if mismatch:
    print(f"    ⚠  {mismatch} Risk_Score mismatches — using derived value")
    rsk["Risk_Score"] = rsk["Risk_Score_Derived"]
rsk = rsk.drop(columns=["Risk_Score_Derived"])

rsk["Is_High_Risk"] = rsk["Risk_Score"] >= 15  # Assumption A8

assert rsk["Risk_ID"].duplicated().sum() == 0, "Duplicate Risk_IDs!"
print(f"  ✓ No duplicate Risk_IDs")
print(f"  Risk_Score range: {rsk['Risk_Score'].min()}–{rsk['Risk_Score'].max()}")
print(f"  High risks (≥15): {rsk['Is_High_Risk'].sum()}")
print(f"  Status distribution:\n{rsk['Status'].value_counts().to_string()}")

out_path = CLEAN_DIR / "risks_clean.csv"
rsk.to_csv(out_path, index=False, date_format="%Y-%m-%d")
print(f"  ✓ Written → {out_path}  ({len(rsk):,} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# 4. REVIEWS
# ══════════════════════════════════════════════════════════════════════════════
section("4 / 4  Cleaning  reviews")

rev = pd.read_csv(RAW_DIR / "reviews.csv", dtype=str)
print(f"  Raw rows: {len(rev):,}")

for col in ["Scheduled_Date", "Completed_Date"]:
    rev[col] = parse_date_col(rev[col], col)

rev["Findings_Count"] = pd.to_numeric(rev["Findings_Count"], errors="coerce").fillna(0).astype(int)

bad = (rev["Completed_Date"].notna() & (rev["Completed_Date"] < rev["Scheduled_Date"])).sum()
if bad:
    print(f"    ⚠  {bad} reviews have Completed_Date < Scheduled_Date — flagging")
rev["Date_Order_Flag"] = (
    rev["Completed_Date"].notna() & (rev["Completed_Date"] < rev["Scheduled_Date"])
)

rev["Is_Overdue"] = (
    rev["Status"].isin(["Planned", "In Progress", "Overdue"])
    & rev["Scheduled_Date"].notna()
    & (rev["Scheduled_Date"] < today)
)

assert rev["Review_ID"].duplicated().sum() == 0, "Duplicate Review_IDs!"
print(f"  ✓ No duplicate Review_IDs")
print(f"  Status distribution:\n{rev['Status'].value_counts().to_string()}")
print(f"  Overdue reviews    : {rev['Is_Overdue'].sum()}")

out_path = CLEAN_DIR / "reviews_clean.csv"
rev.to_csv(out_path, index=False, date_format="%Y-%m-%d")
print(f"  ✓ Written → {out_path}  ({len(rev):,} rows)")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
section("DONE  —  All clean files written to data/clean/")
print("""
  Defects  → defects_clean.csv
  Issues   → issues_clean.csv   [SYNTHETIC]
  Risks    → risks_clean.csv    [SYNTHETIC]
  Reviews  → reviews_clean.csv  [SYNTHETIC]

  Key decisions applied:
    • Severity 1-4 mapped to Critical/High/Medium/Low
    • Status nulls inferred from Is_Closed flag
    • Deferred tracked separately (not Open, not Closed)
    • Resolution_Time_Original preserved; Resolution_Days recalculated
    • SLA_Target_Days: Critical=2, High=5, Medium=10, Low=20
    • Is_Overdue derived for open defects/issues/reviews past SLA/due date
    • High Risk = Risk_Score >= 15 (Probability x Impact, max 25)
""")
