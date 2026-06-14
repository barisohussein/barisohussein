# ─── Imports & File Path ───────────────────────────────────────────────────────

import pandas as pd
import json
import os
import glob
from datetime import datetime

# Auto-detect the CSV in the data/ folder (relative to this script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_files = glob.glob(os.path.join(BASE_DIR, "data", "Chase*.CSV")) + \
            glob.glob(os.path.join(BASE_DIR, "data", "Chase*.csv"))

if not csv_files:
    raise FileNotFoundError("No Chase CSV found in the data/ folder.")

# Chase filenames contain the date (e.g. Chase8872_Activity_20260614.CSV) — latest sorts last
file_path = sorted(csv_files)[-1]
print(f"📂 Reading: {file_path}")



# ─── Load & Clean ─────────────────────────────────────────────────────────────

df = pd.read_csv(file_path, engine="python", skiprows=1)
df = df.iloc[:, :-1]
df.columns = ["Details", "Posting Date", "Description", "Amount", "Type", "Balance","Extra"]

# ─── Parse Dates & Amounts ────────────────────────────────────────────────────

df["Posting Date"] = pd.to_datetime(df["Posting Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Posting Date", "Amount"])

# ─── Filter Ignored Transactions ──────────────────────────────────────────────

IGNORE_KEYWORDS = ["TRANSFER", "KCHA"]

def should_ignore(desc):
    desc = str(desc).upper()
    return any(kw.upper() in desc for kw in IGNORE_KEYWORDS)

df = df[~df["Description"].apply(should_ignore)]

# ─── Categorization ───────────────────────────────────────────────────────────

def categorize(desc):
    desc = str(desc).upper()

    if "PAYROLL" in desc or "ORIG CO NAME" in desc:
        return "Income"
    elif any(x in desc for x in ["WAL-MART", "DOLLARTREE", "RESTAURANT DEPOT", "WALMART",
                                   "GROCERY", "SAFEWAY", "COSTCO", "QFC", "TRADER JOE",
                                   "WHOLE FOODS", "FRED MEYER", "ALBERTSONS"]):
        return "Groceries"
    elif any(x in desc for x in ["DAVESHOTCHICKEN", "CHICK-FIL-A", "YARD HOUSE", "WENDYS",
                                   "SUBWAY", "CHIPOTLE", "POKE", "STARBUCKS", "MCDONALD",
                                   "PIZZA", "SUSHI", "WINGSTOP", "DOMINO", "POTBELLY",
                                   "HOT CHICK", "SHAWARMA", "PACK FOOD", "ALADDIN", "BOBA",
                                   "CRUSH", "CHIC", "GRILL", "FOGO", "INSOMNIA", "VENDING",
                                   "TERIYAKI", "RESTAURANT", "CAFE", "FOB"]):
        return "Restaurants"
    elif any(x in desc for x in ["TIRE", "JIFFY LUBE", "GAS", "SHELL", "CHEVRON", "ARCO",
                                   "FUEL1508", "FUEL1563", "FUEL", "ORCA", "PAYBYPHONE",
                                   "PARKING", "METROPOLIS", "SDOT", "UBER", "LYFT", "TRANSIT"]):
        return "Transportation"
    elif any(x in desc for x in ["CHASE CREDIT CRD AUTOPAY"]):
        return "Credit Card"
    elif any(x in desc for x in ["INS PREM", "GEICO", "PROGRESSIVE", "ALLSTATE", "PROG DIRECT"]):
        return "Insurance"
    elif any(x in desc for x in ["AMAZON", "TARGET", "WALMART", "MKTPL"]):
        return "Shopping"
    elif any(x in desc for x in ["YUSUF", "NAZIRA", "BILAL", "ZELLE", "VENMO"]):
        return "Family Support"
    elif any(x in desc for x in ["GoFundMe", "MUSLIM ASSOCIATION", "MASJID", "MOSQUE"]):
        return "Donations"
    elif any(x in desc for x in ["AMC", "NETFLIX", "SPOTIFY", "HULU", "DISNEY", "YOUTUBE"]):
        return "Entertainment"
    elif any(x in desc for x in ["COMCAST", "T-MOBILE", "VERIZON", "AT&T", "ELECTRIC", "INTERNET"]):
        return "Utilities"
    elif any(x in desc for x in ["BILT", "LIGHT"]):
        return "Apartment"
    return "Other"

df["Category"] = df["Description"].apply(categorize)
df["Month"] = df["Posting Date"].dt.to_period("M")

# ─── Summaries ────────────────────────────────────────────────────────────────

income = df[df["Amount"] > 0].groupby("Month")["Amount"].sum()
expenses = df[df["Amount"] < 0].groupby("Month")["Amount"].sum().abs()

monthly = pd.concat([income, expenses], axis=1)
monthly.columns = ["Income", "Expenses"]
monthly["Savings"] = monthly["Income"] - monthly["Expenses"]

category_summary = (
    df[(df["Amount"] < 0) & (df["Category"] != "Income")]
    .groupby("Category")["Amount"]
    .sum()
    .abs()
    .sort_values(ascending=False)
)

# ─── Build Transaction Lists ───────────────────────────────────────────────────

expense_tx = (
    df[(df["Amount"] < 0) & (df["Category"] != "Income")]
    .sort_values("Posting Date", ascending=False)[["Posting Date", "Description", "Amount", "Type", "Category"]]
    .copy()
)
expense_tx["Posting Date"] = expense_tx["Posting Date"].dt.strftime("%Y-%m-%d")
expense_tx["Amount"] = expense_tx["Amount"].abs().round(2)
expense_tx["Description"] = expense_tx["Description"].str.strip().str[:50]

income_tx = (
    df[df["Category"] == "Income"]
    .sort_values("Posting Date", ascending=False)[["Posting Date", "Description", "Amount", "Type", "Category"]]
    .copy()
)
income_tx["Posting Date"] = income_tx["Posting Date"].dt.strftime("%Y-%m-%d")
income_tx["Amount"] = (income_tx["Amount"].abs() * -1).round(2)
income_tx["Description"] = income_tx["Description"].str.strip().str[:50]

recent_tx = pd.concat([expense_tx, income_tx]).sort_values("Posting Date", ascending=False)

daily_spend = (
    df[df["Amount"] < 0]
    .groupby("Posting Date")["Amount"]
    .sum()
    .abs()
    .reset_index()
)
daily_spend["Posting Date"] = daily_spend["Posting Date"].dt.strftime("%Y-%m-%d")

# ─── Export JSON ──────────────────────────────────────────────────────────────

dashboard_data = {
    "monthly": {
        "labels":   [str(m) for m in monthly.index],
        "income":   monthly["Income"].round(2).tolist(),
        "expenses": monthly["Expenses"].round(2).tolist(),
        "savings":  monthly["Savings"].round(2).tolist(),
    },
    "categories": {
        "labels": category_summary.index.tolist(),
        "values": category_summary.round(2).tolist(),
    },
    "daily": {
        "dates":  daily_spend["Posting Date"].tolist(),
        "values": daily_spend["Amount"].round(2).tolist(),
    },
    "transactions": recent_tx.to_dict(orient="records"),
    "totals": {
        "total_income":        round(float(income.sum()), 2),
        "total_expenses":      round(float(expenses.sum()), 2),
        "total_savings":       round(float(income.sum() - expenses.sum()), 2),
        "top_category":        category_summary.index[0] if len(category_summary) else "N/A",
        "top_category_amount": round(float(category_summary.iloc[0]), 2) if len(category_summary) else 0,
    }
}
# Output to docs/ folder so dashboard.html can load it
json_out = os.path.join(BASE_DIR, "docs", "dashboard_data.json")

os.makedirs(os.path.dirname(json_out), exist_ok=True)

with open(json_out, "w") as f:
    json.dump(dashboard_data, f, indent=2)

print(f"\n✅ Dashboard data exported → {json_out}")
